from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserIdiomProgress(Base):
    __tablename__ = "user_idiom_progress"
    __table_args__ = (UniqueConstraint("user_id", "idiom_id", name="uq_user_idiom"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    idiom_id: Mapped[int] = mapped_column(Integer, ForeignKey("idioms.id"), nullable=False, index=True)
    box_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
