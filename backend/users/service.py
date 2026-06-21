from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from users.models import User


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_tg_id(db: AsyncSession, tg_id: int) -> User | None:
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()


async def get_or_create_by_tg(db: AsyncSession, tg_id: int, username: str | None, first_name: str | None) -> User:
    user = await get_user_by_tg_id(db, tg_id)
    if not user:
        user = User(tg_id=tg_id, username=username, first_name=first_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
