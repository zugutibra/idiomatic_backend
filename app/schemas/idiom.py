from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.idiom import Difficulty, Topic


class IdiomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phrase: str
    meaning: str
    example_sentence: str
    topic: Topic
    difficulty: Difficulty
    translation_ru: str | None = None
    translation_kk: str | None = None


class IdiomWithStatus(IdiomRead):
    box_level: int
    is_new: bool


class NextDueRead(BaseModel):
    next_review_at: datetime | None = None


class QuizOption(BaseModel):
    text: str
    is_correct: bool


class QuizQuestion(BaseModel):
    idiom_id: int
    phrase: str
    options: list[QuizOption]
