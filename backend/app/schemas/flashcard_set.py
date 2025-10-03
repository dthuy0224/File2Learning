from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FlashcardSet(BaseModel):
    id: int
    title: Optional[str]
    original_filename: str
    card_count: int
    created_at: datetime

    class Config:
        from_attributes = True
