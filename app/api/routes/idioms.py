import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.leitner import next_box_level, next_review_at
from app.models.idiom import Idiom, Topic
from app.models.progress import UserIdiomProgress
from app.models.user import User
from app.schemas.idiom import IdiomRead, IdiomWithStatus, NextDueRead, QuizOption, QuizQuestion
from app.schemas.progress import ProgressRead, ReviewSubmit

router = APIRouter(prefix="/idioms", tags=["idioms"])


@router.get("", response_model=list[IdiomRead])
def list_idioms(topic: Topic | None = Query(default=None), db: Session = Depends(get_db)) -> list[Idiom]:
    query = db.query(Idiom)
    if topic is not None:
        query = query.filter(Idiom.topic == topic)
    return query.order_by(Idiom.id).all()


@router.get("/due", response_model=list[IdiomWithStatus])
def get_due_idioms(
    topic: Topic | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IdiomWithStatus]:
    now = datetime.now(timezone.utc)
    idiom_query = db.query(Idiom)
    if topic is not None:
        idiom_query = idiom_query.filter(Idiom.topic == topic)
    idioms = idiom_query.order_by(Idiom.id).all()

    progress_by_idiom = {
        p.idiom_id: p
        for p in db.query(UserIdiomProgress).filter(UserIdiomProgress.user_id == current_user.id).all()
    }

    due: list[IdiomWithStatus] = []
    for idiom in idioms:
        progress = progress_by_idiom.get(idiom.id)
        if progress is None:
            due.append(IdiomWithStatus(**IdiomRead.model_validate(idiom).model_dump(), box_level=1, is_new=True))
        elif progress.next_review_at is not None and progress.next_review_at.replace(tzinfo=timezone.utc) <= now:
            due.append(
                IdiomWithStatus(
                    **IdiomRead.model_validate(idiom).model_dump(), box_level=progress.box_level, is_new=False
                )
            )
    return due


@router.get("/next-due", response_model=NextDueRead)
def get_next_due(
    topic: Topic | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NextDueRead:
    query = (
        db.query(UserIdiomProgress)
        .join(Idiom, Idiom.id == UserIdiomProgress.idiom_id)
        .filter(UserIdiomProgress.user_id == current_user.id, UserIdiomProgress.next_review_at.isnot(None))
    )
    if topic is not None:
        query = query.filter(Idiom.topic == topic)
    next_progress = query.order_by(UserIdiomProgress.next_review_at.asc()).first()
    return NextDueRead(next_review_at=next_progress.next_review_at if next_progress else None)


@router.post("/{idiom_id}/review", response_model=ProgressRead)
def submit_review(
    idiom_id: int,
    payload: ReviewSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserIdiomProgress:
    idiom = db.get(Idiom, idiom_id)
    if idiom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idiom not found")

    progress = (
        db.query(UserIdiomProgress)
        .filter(UserIdiomProgress.user_id == current_user.id, UserIdiomProgress.idiom_id == idiom_id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if progress is None:
        progress = UserIdiomProgress(
            user_id=current_user.id, idiom_id=idiom_id, box_level=1, times_correct=0, times_seen=0
        )
        db.add(progress)

    progress.box_level = next_box_level(progress.box_level, payload.correct)
    progress.last_reviewed_at = now
    progress.next_review_at = next_review_at(progress.box_level, now)
    progress.times_seen += 1
    if payload.correct:
        progress.times_correct += 1

    db.commit()
    db.refresh(progress)
    return progress


@router.get("/{idiom_id}/quiz-options", response_model=QuizQuestion)
def get_quiz_options(idiom_id: int, db: Session = Depends(get_db)) -> QuizQuestion:
    idiom = db.get(Idiom, idiom_id)
    if idiom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idiom not found")

    distractor_pool = db.query(Idiom).filter(Idiom.topic == idiom.topic, Idiom.id != idiom.id).all()
    if len(distractor_pool) < 3:
        distractor_pool = db.query(Idiom).filter(Idiom.id != idiom.id).all()

    distractors = random.sample(distractor_pool, k=min(3, len(distractor_pool)))
    options = [QuizOption(text=idiom.meaning, is_correct=True)] + [
        QuizOption(text=d.meaning, is_correct=False) for d in distractors
    ]
    random.shuffle(options)

    return QuizQuestion(idiom_id=idiom.id, phrase=idiom.phrase, options=options)
