from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.idiom import Idiom, Topic
from app.models.progress import UserIdiomProgress
from app.models.user import User
from app.schemas.progress import ProgressStats, TopicStat

router = APIRouter(prefix="/progress", tags=["progress"])

MASTERED_BOX = 5


def _compute_streak_days(review_dates: set) -> int:
    if not review_dates:
        return 0
    today = datetime.now(timezone.utc).date()
    streak = 0
    cursor = today
    while cursor in review_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


@router.get("/stats", response_model=ProgressStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ProgressStats:
    now = datetime.now(timezone.utc)
    total_idioms = db.query(Idiom).count()

    progress_rows = db.query(UserIdiomProgress).filter(UserIdiomProgress.user_id == current_user.id).all()
    progress_by_idiom_id = {p.idiom_id: p for p in progress_rows}

    total_seen = len(progress_rows)
    mastered = sum(1 for p in progress_rows if p.box_level >= MASTERED_BOX)
    due_today = sum(
        1
        for p in progress_rows
        if p.next_review_at is not None and p.next_review_at.replace(tzinfo=timezone.utc) <= now
    )
    new_count = total_idioms - total_seen
    due_today += new_count

    review_dates = {
        p.last_reviewed_at.date() for p in progress_rows if p.last_reviewed_at is not None
    }
    streak_days = _compute_streak_days(review_dates)

    topics: list[TopicStat] = []
    for topic in Topic:
        topic_idioms = db.query(Idiom).filter(Idiom.topic == topic).all()
        topic_total = len(topic_idioms)
        if topic_total == 0:
            continue
        topic_mastered = sum(
            1
            for idiom in topic_idioms
            if (p := progress_by_idiom_id.get(idiom.id)) is not None and p.box_level >= MASTERED_BOX
        )
        pct = round((topic_mastered / topic_total) * 100)
        topics.append(TopicStat(topic=topic.value, total=topic_total, mastered=topic_mastered, pct=pct))

    return ProgressStats(
        total_seen=total_seen,
        total_idioms=total_idioms,
        mastered=mastered,
        due_today=due_today,
        streak_days=streak_days,
        topics=topics,
    )
