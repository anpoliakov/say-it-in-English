"""Auth middleware.

DEV_MODE=true  → принимает заголовок X-Dev-User-Id (int).
                 Если не передан — автоматически создаёт/возвращает dev-пользователя id=1.
DEV_MODE=false → проверяет Telegram initData (HMAC-SHA256).
"""
import hashlib
import hmac
import urllib.parse
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_db
from models import User
from settings import settings

async def _get_or_create_dev_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.tg_id == None).limit(1))  # noqa: E711
    user = result.scalar_one_or_none()
    if not user:
        user = User(tg_id=None, username="dev", first_name="Developer")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def get_current_user(
    x_dev_user_id: int | None = Header(default=None),
    x_tg_init_data: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if settings.dev_mode:
        return await _get_or_create_dev_user(db)

    # --- Production: validate Telegram initData ---
    if not x_tg_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram auth")

    data = dict(urllib.parse.parse_qsl(x_tg_init_data))
    received_hash = data.pop("hash", "")
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret = hmac.new(
        hmac.new(b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256).digest(),
        data_check.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(secret, received_hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")

    import json
    tg_user = json.loads(data.get("user", "{}"))
    tg_id = tg_user.get("id")
    if not tg_id:
        raise HTTPException(status_code=401, detail="No user in initData")

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
