import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.exceptions import WordNotFound
from game.models import GameSession
from game.schemas import SessionOut, RoundWord, FinishSessionIn
from users.models import User
from words.models import Word
from words.schemas import WordOut
from storage import get_storage

MIN_WORDS_FOR_GAME = 4  # минимум слов для запуска игры


def _word_to_out(w: Word) -> WordOut:
    return WordOut(
        id=w.id, en=w.en, ru=w.ru,
        category=w.category,
        image_url=get_storage().get_url(w.image_key),
        source=w.source,
        created_at=w.created_at,
    )


async def start_session(db: AsyncSession, user: User) -> SessionOut:
    """Create a new game session for the user."""
    session = GameSession(user_id=user.id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut.model_validate(session)


async def finish_session(
    db: AsyncSession,
    user: User,
    session_id: int,
    result: FinishSessionIn,
) -> SessionOut:
    """Mark session as finished, save score."""
    res = await db.execute(
        select(GameSession).where(
            GameSession.id == session_id,
            GameSession.user_id == user.id,
            GameSession.finished_at.is_(None),
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise WordNotFound()  # используем SessionNotFound позже

    session.score = result.score
    session.words_done = result.words_done
    session.finished_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return SessionOut.model_validate(session)


async def get_round(
    db: AsyncSession,
    user: User,
    count: int = 10,
) -> list[RoundWord]:
    """Возвращает `count` случайных слов для раунда с 4 вариантами ответа каждое."""
    # Загружаем count + 3 слов чтобы всегда были декой
    need = max(count + 3, MIN_WORDS_FOR_GAME)
    res = await db.execute(
        select(Word)
        .where(Word.user_id == user.id)
        .order_by(func.random())
        .limit(need)
    )
    all_words = res.scalars().all()

    if len(all_words) < MIN_WORDS_FOR_GAME:
        raise WordNotFound()  # недостаточно слов для игры

    quiz_words = all_words[:count]
    all_ru = [w.ru for w in all_words]

    rounds: list[RoundWord] = []
    for word in quiz_words:
        decoys = random.sample([r for r in all_ru if r != word.ru], min(3, len(all_ru) - 1))
        choices = decoys + [word.ru]
        random.shuffle(choices)
        rounds.append(RoundWord(
            word=_word_to_out(word),
            choices=choices,
            correct=word.ru,
        ))

    return rounds


async def get_history(db: AsyncSession, user: User, limit: int = 20) -> list[SessionOut]:
    """Last N finished sessions, newest first."""
    res = await db.execute(
        select(GameSession)
        .where(
            GameSession.user_id == user.id,
            GameSession.finished_at.isnot(None),
        )
        .order_by(GameSession.finished_at.desc())
        .limit(limit)
    )
    return [SessionOut.model_validate(s) for s in res.scalars().all()]
