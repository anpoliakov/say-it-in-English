from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from users.models import User
from users.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)) -> UserOut:
    return user
