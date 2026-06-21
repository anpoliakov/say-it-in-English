from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.dependencies import get_current_user
from users.models import User
from game.schemas import SessionOut, RoundWord, FinishSessionIn
import game.service as svc

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def start_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new game session."""
    return await svc.start_session(db, user)


@router.post("/sessions/{session_id}/finish", response_model=SessionOut)
async def finish_session(
    session_id: int,
    result: FinishSessionIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit score and finish the session."""
    return await svc.finish_session(db, user, session_id=session_id, result=result)


@router.get("/round", response_model=list[RoundWord])
async def get_round(
    count: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get N random words with answer choices for a quiz round."""
    return await svc.get_round(db, user, count=count)


@router.get("/history", response_model=list[SessionOut])
async def get_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get last N finished game sessions."""
    return await svc.get_history(db, user, limit=limit)
