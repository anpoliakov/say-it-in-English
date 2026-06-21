import uuid
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import WordNotFound, DuplicateWord
from storage import get_storage
from users.models import User
from words.models import Word, WordCategory
from words.schemas import WordOut, WordUpdate


def _to_out(w: Word) -> WordOut:
    return WordOut(
        id=w.id,
        en=w.en,
        ru=w.ru,
        category=w.category,
        image_url=get_storage().get_url(w.image_key),
        source=w.source,
        created_at=w.created_at,
    )


async def list_words(
    db: AsyncSession,
    user: User,
    limit: int = 100,
    offset: int = 0,
) -> list[WordOut]:
    result = await db.execute(
        select(Word)
        .where(Word.user_id == user.id)
        .order_by(Word.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_to_out(w) for w in result.scalars().all()]


async def create_word(
    db: AsyncSession,
    user: User,
    en: str,
    ru: str = "—",
    category: WordCategory = WordCategory.other,
    image: Optional[UploadFile] = None,
) -> WordOut:
    en_upper = en.strip().upper()

    existing = await db.execute(
        select(Word).where(Word.user_id == user.id, Word.en == en_upper)
    )
    if existing.scalar_one_or_none():
        raise DuplicateWord()

    image_key = None
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else "jpg"
        image_key = f"{user.id}/{uuid.uuid4()}.{ext}"
        data = await image.read()
        get_storage().upload(image_key, data, image.content_type or "image/jpeg")

    word = Word(user_id=user.id, en=en_upper, ru=ru.strip(), category=category, image_key=image_key)
    db.add(word)
    await db.commit()
    await db.refresh(word)
    return _to_out(word)


async def update_word(
    db: AsyncSession,
    user: User,
    word_id: int,
    data: WordUpdate,
) -> WordOut:
    result = await db.execute(select(Word).where(Word.id == word_id, Word.user_id == user.id))
    word = result.scalar_one_or_none()
    if not word:
        raise WordNotFound()

    if data.ru is not None:
        word.ru = data.ru.strip()
    if data.category is not None:
        word.category = data.category

    await db.commit()
    await db.refresh(word)
    return _to_out(word)


async def update_word_image(
    db: AsyncSession,
    user: User,
    word_id: int,
    image: UploadFile,
) -> WordOut:
    result = await db.execute(select(Word).where(Word.id == word_id, Word.user_id == user.id))
    word = result.scalar_one_or_none()
    if not word:
        raise WordNotFound()

    if word.image_key:
        get_storage().delete(word.image_key)

    ext = image.filename.rsplit(".", 1)[-1].lower() if image.filename and "." in image.filename else "jpg"
    key = f"{user.id}/{uuid.uuid4()}.{ext}"
    data = await image.read()
    get_storage().upload(key, data, image.content_type or "image/jpeg")
    word.image_key = key

    await db.commit()
    await db.refresh(word)
    return _to_out(word)


async def delete_word(db: AsyncSession, user: User, word_id: int) -> None:
    result = await db.execute(select(Word).where(Word.id == word_id, Word.user_id == user.id))
    word = result.scalar_one_or_none()
    if not word:
        raise WordNotFound()
    if word.image_key:
        get_storage().delete(word.image_key)
    await db.delete(word)
    await db.commit()
