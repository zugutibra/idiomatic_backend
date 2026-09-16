"""One-time script to populate the idioms table from data/idioms_seed.json.

Usage: python -m scripts.seed_idioms
"""

import json
from pathlib import Path

from app.db.base_all import Base
from app.db.session import SessionLocal, engine
from app.models.idiom import Idiom

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "idioms_seed.json"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    entries = json.loads(SEED_FILE.read_text())

    db = SessionLocal()
    try:
        existing_phrases = {phrase for (phrase,) in db.query(Idiom.phrase).all()}
        added = 0
        for entry in entries:
            if entry["phrase"] in existing_phrases:
                continue
            db.add(Idiom(**entry))
            added += 1
        db.commit()
        print(f"Seeded {added} new idioms ({len(entries) - added} already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
