from typing import Iterable
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.label import Label

def ensure_slots(db: Session, slots: Iterable[int] = range(1, 11)) -> int:
    try:
        existing_slots = set(db.execute(select(Label.slot)).scalars().all())
        to_create = [Label(slot=s, text="") for s in slots if s not in existing_slots]
        if to_create:
            db.add_all(to_create)
            db.commit()
        return len(to_create)
    except SQLAlchemyError:
        db.rollback()
        return 0