from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("slot", name="uq_labels_slot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slot: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(length=10), nullable=False, default="")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:  # helpful when debugging in the shell
        return f"<Label id={self.id} slot={self.slot} text={self.text!r}>"