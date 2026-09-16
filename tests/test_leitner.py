from datetime import datetime

from app.core.leitner import MAX_BOX, MIN_BOX, next_box_level, next_review_at


def test_correct_answer_moves_up_a_box():
    assert next_box_level(1, correct=True) == 2
    assert next_box_level(3, correct=True) == 4


def test_correct_answer_caps_at_max_box():
    assert next_box_level(MAX_BOX, correct=True) == MAX_BOX


def test_incorrect_answer_resets_to_box_one():
    assert next_box_level(4, correct=False) == MIN_BOX
    assert next_box_level(MAX_BOX, correct=False) == MIN_BOX


def test_review_intervals_double_by_box():
    now = datetime(2026, 1, 1)
    assert (next_review_at(1, now) - now).days == 1
    assert (next_review_at(2, now) - now).days == 3
    assert (next_review_at(3, now) - now).days == 7
    assert (next_review_at(4, now) - now).days == 14
    assert (next_review_at(5, now) - now).days == 30
