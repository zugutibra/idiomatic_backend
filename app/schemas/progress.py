from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewSubmit(BaseModel):
    correct: bool


class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idiom_id: int
    box_level: int
    last_reviewed_at: datetime | None
    next_review_at: datetime | None
    times_correct: int
    times_seen: int


class TopicStat(BaseModel):
    topic: str
    total: int
    mastered: int
    pct: int


class ProgressStats(BaseModel):
    total_seen: int
    total_idioms: int
    mastered: int
    due_today: int
    streak_days: int
    topics: list[TopicStat]
