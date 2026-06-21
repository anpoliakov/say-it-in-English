from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from words.schemas import WordOut


class SessionOut(BaseModel):
    id: int
    score: int
    words_done: int
    started_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


class RoundWord(BaseModel):
    """One word for the quiz round: correct answer + 3 decoys."""
    word: WordOut
    choices: list[str]  # 4 Russian translations, shuffled
    correct: str        # correct Russian translation


class FinishSessionIn(BaseModel):
    score: int
    words_done: int
