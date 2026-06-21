import enum

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class WordCategory(str, enum.Enum):
    noun = "noun"
    verb = "verb"
    adj = "adj"
    adv = "adv"
    phrase = "phrase"
    other = "other"


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    en: Mapped[str] = mapped_column(String(256))
    ru: Mapped[str] = mapped_column(String(256), default="—")
    category: Mapped[WordCategory] = mapped_column(SAEnum(WordCategory), default=WordCategory.other)
    image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="manual")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["users.models.User"] = relationship(back_populates="words")
