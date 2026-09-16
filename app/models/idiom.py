import enum

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Topic(str, enum.Enum):
    education = "education"
    environment = "environment"
    technology = "technology"
    relationships = "relationships"
    work = "work"
    travel = "travel"
    health = "health"
    culture = "culture"


class Difficulty(str, enum.Enum):
    easier = "easier"
    intermediate = "intermediate"
    advanced = "advanced"


class Idiom(Base):
    __tablename__ = "idioms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phrase: Mapped[str] = mapped_column(String(255), nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    example_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[Topic] = mapped_column(Enum(Topic), nullable=False, index=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.intermediate, nullable=False)
    translation_ru: Mapped[str | None] = mapped_column(String(255), nullable=True)
    translation_kk: Mapped[str | None] = mapped_column(String(255), nullable=True)
