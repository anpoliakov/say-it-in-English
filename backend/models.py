from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db import Base
import enum

class WordCategory(str, enum.Enum):
    noun   = "noun"
    verb   = "verb"
    adj    = "adj"
    adv    = "adv"
    phrase = "phrase"
    other  = "other"

class User(Base):
    __tablename__ = "users"
    id         : Mapped[int]  = mapped_column(BigInteger, primary_key=True)
    tg_id      : Mapped[int | None]  = mapped_column(BigInteger, unique=True, nullable=True)
    username   : Mapped[str | None]  = mapped_column(String(64))
    first_name : Mapped[str | None]  = mapped_column(String(128))
    created_at : Mapped[DateTime]    = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at : Mapped[DateTime]    = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    words    : Mapped[list["Word"]]        = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions : Mapped[list["GameSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"
    id         : Mapped[int]  = mapped_column(BigInteger, primary_key=True)
    user_id    : Mapped[int]  = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    en         : Mapped[str]  = mapped_column(String(256))
    ru         : Mapped[str]  = mapped_column(String(256), default="—")
    category   : Mapped[WordCategory] = mapped_column(SAEnum(WordCategory), default=WordCategory.other)
    image_key  : Mapped[str | None]   = mapped_column(String(512), nullable=True)
    source     : Mapped[str]  = mapped_column(String(32), default="manual")
    created_at : Mapped[DateTime]     = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="words")

class GameSession(Base):
    __tablename__ = "game_sessions"
    id          : Mapped[int]  = mapped_column(BigInteger, primary_key=True)
    user_id     : Mapped[int]  = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    score       : Mapped[int]  = mapped_column(Integer, default=0)
    words_done  : Mapped[int]  = mapped_column(Integer, default=0)
    started_at  : Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at : Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")
