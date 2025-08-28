from fastapi import APIRouter, Depends, HTTPException, Path # type: ignore
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models.label import Label
from app.schemas import LabelOut, LabelIn, LabelBulkIn

router = APIRouter(prefix="/labels", tags=["labels"])

@router.get("", response_model=List[LabelOut])
def list_labels(db: Session = Depends(get_db)):
    rows = db.query(Label).order_by(Label.slot).all()
    return [LabelOut.model_validate(r) for r in rows]

@router.put("/{slot}", response_model=LabelOut)
def update_label(
    slot: int = Path(..., ge=1, le=10, description="Slot 1..10"),
    payload: LabelIn = ..., # type: ignore
    db: Session = Depends(get_db),
):
    row = db.query(Label).filter_by(slot=slot).one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail=f"Slot {slot} not found")
    row.text = payload.text
    db.commit()
    db.refresh(row)
    return LabelOut.model_validate(row)

@router.put("", response_model=List[LabelOut])
def bulk_upsert(payload: LabelBulkIn, db: Session = Depends(get_db)):
    slots = [i.slot for i in payload.items]
    if len(slots) != len(set(slots)):
        raise HTTPException(status_code=400, detail="Duplicate slots in payload")
    out: list[LabelOut] = []
    for item in payload.items:
        row = db.query(Label).filter_by(slot=item.slot).one_or_none()
        if not row:
            row = Label(slot=item.slot, text=item.text)
            db.add(row)
        else:
            row.text = item.text
        db.flush()  
        out.append(LabelOut.model_validate(row))
    db.commit()
    return out