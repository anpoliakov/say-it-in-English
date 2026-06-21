from pydantic import BaseModel
from datetime import datetime


class UserOut(BaseModel):
    id: int
    tg_id: int | None
    username: str | None
    first_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
