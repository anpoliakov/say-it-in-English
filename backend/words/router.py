from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from auth.dependencies import get_current_user
from users.models import User
from words.models import WordCategory
from words.schemas import WordOut, WordUpdate
import words.service as svc

router = APIRouter(prefix="/words", tags=["words"])


@router.get("", response_model=list[WordOut])
async def list_words(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_words(db, user, limit=limit, offset=offset)


@router.post("", response_model=WordOut, status_code=201)
async def create_word(
    en: str = Form(...),
    ru: str = Form(default="—"),
    category: WordCategory = Form(default=WordCategory.other),
    image: Optional[UploadFile] = File(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_word(db, user, en=en, ru=ru, category=category, image=image)


@router.patch("/{word_id}", response_model=WordOut)
async def update_word(
    word_id: int,
    data: WordUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_word(db, user, word_id=word_id, data=data)


@router.patch("/{word_id}/image", response_model=WordOut)
async def update_word_image(
    word_id: int,
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_word_image(db, user, word_id=word_id, image=image)


@router.delete("/{word_id}", status_code=204)
async def delete_word(
    word_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await svc.delete_word(db, user, word_id=word_id)
