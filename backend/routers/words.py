from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional
import uuid

from db import get_db
from models import Word, WordCategory, User
from auth import get_current_user
import storage

router = APIRouter(prefix="/words", tags=["words"])

# ── Schemas ──────────────────────────────────────────────
class WordOut(BaseModel):
    id: int
    en: str
    ru: str
    category: WordCategory
    image_url: Optional[str]
    source: str

    class Config:
        from_attributes = True

# ── GET /words ────────────────────────────────────────────
@router.get("", response_model=list[WordOut])
async def list_words(
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Word).where(Word.user_id == user.id).order_by(Word.created_at.desc())
    )
    words = result.scalars().all()
    return [
        WordOut(
            id=w.id, en=w.en, ru=w.ru,
            category=w.category,
            image_url=storage.get_image_url(w.image_key),
            source=w.source,
        )
        for w in words
    ]

# ── POST /words ───────────────────────────────────────────
@router.post("", response_model=WordOut, status_code=201)
async def create_word(
    en:       str = Form(...),
    ru:       str = Form(default="—"),
    category: WordCategory = Form(default=WordCategory.other),
    image:    UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    en_upper = en.strip().upper()
    # Check duplicate
    existing = await db.execute(
        select(Word).where(Word.user_id == user.id, Word.en == en_upper)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Word already exists")

    image_key = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else "jpg"
        image_key = f"{user.id}/{uuid.uuid4()}.{ext}"
        data = await image.read()
        storage.upload_image(image_key, data, image.content_type or "image/jpeg")

    word = Word(
        user_id=user.id, en=en_upper, ru=ru.strip(),
        category=category, image_key=image_key, source="manual"
    )
    db.add(word)
    await db.commit()
    await db.refresh(word)
    return WordOut(
        id=word.id, en=word.en, ru=word.ru,
        category=word.category,
        image_url=storage.get_image_url(word.image_key),
        source=word.source,
    )

# ── DELETE /words/{word_id} ───────────────────────────────
@router.delete("/{word_id}", status_code=204)
async def delete_word(
    word_id: int,
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Word).where(Word.id == word_id, Word.user_id == user.id)
    )
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    if word.image_key:
        storage.delete_image(word.image_key)
    await db.delete(word)
    await db.commit()

# ── PATCH /words/{word_id}/image ─────────────────────────
@router.patch("/{word_id}/image", response_model=WordOut)
async def update_word_image(
    word_id: int,
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Word).where(Word.id == word_id, Word.user_id == user.id)
    )
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    if word.image_key:
        storage.delete_image(word.image_key)

    ext = image.filename.rsplit(".", 1)[-1].lower() if image.filename and "." in image.filename else "jpg"
    key = f"{user.id}/{uuid.uuid4()}.{ext}"
    data = await image.read()
    storage.upload_image(key, data, image.content_type or "image/jpeg")
    word.image_key = key
    await db.commit()
    await db.refresh(word)
    return WordOut(
        id=word.id, en=word.en, ru=word.ru,
        category=word.category,
        image_url=storage.get_image_url(word.image_key),
        source=word.source,
    )
