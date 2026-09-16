from datetime import datetime, timedelta

BOX_INTERVALS_DAYS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
MIN_BOX = 1
MAX_BOX = 5


def next_box_level(current_box: int, correct: bool) -> int:
    if correct:
        return min(current_box + 1, MAX_BOX)
    return MIN_BOX


def next_review_at(box_level: int, now: datetime) -> datetime:
    days = BOX_INTERVALS_DAYS[box_level]
    return now + timedelta(days=days)
