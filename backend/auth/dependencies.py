"""FastAPI dependency: get_current_user.
Делегирует логику в dev.py или telegram.py в зависимости от DEV_MODE.
"""
from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.database import get_db
from core.exceptions import Unauthorized
from users.models import User
from auth.dev import get_or_create_dev_user
from auth.telegram import verify_init_data


async def get_current_user(
    x_tg_init_data: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if settings.dev_mode:
        return await get_or_create_dev_user(db)

    if not x_tg_init_data:
        raise Unauthorized("Missing Telegram auth")

    tg_user = verify_init_data(x_tg_init_data)
    tg_id = tg_user["id"]

    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            tg_id=tg_id,
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
