from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from words.models import WordCategory


class WordOut(BaseModel):
    id: int
    en: str
    ru: str
    category: WordCategory
    image_url: Optional[str]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class WordUpdate(BaseModel):
    """PATCH /words/{id} — все поля опциональные."""
    ru: Optional[str] = None
    category: Optional[WordCategory] = None
