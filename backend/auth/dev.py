"""Dev stub: автоматически создаёт / возвращает dev-пользователя без Telegram."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from users.models import User


async def get_or_create_dev_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.tg_id.is_(None)).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        user = User(tg_id=None, username="dev", first_name="Developer")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
