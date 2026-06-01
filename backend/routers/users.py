from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models import User
from auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserOut(BaseModel):
    id: int
    tg_id: int | None
    username: str | None
    first_name: str | None

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
