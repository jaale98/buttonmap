from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LabelOut(BaseModel):
    slot: int = Field(..., ge=1, le=10, description="Button slot index (1..10)")
    text: str = Field(..., max_length=10)
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LabelIn(BaseModel):
    text: str = Field(..., max_length=10)

class LabelBulkItem(BaseModel):
    slot: int = Field(..., ge=1, le=10)
    text: str = Field(..., max_length=10)

class LabelBulkIn(BaseModel):
    items: list[LabelBulkItem]