from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# Shared properties
class FlashcardBase(BaseModel):
    front_text: str
    back_text: str
    example_sentence: Optional[str] = None
    pronunciation: Optional[str] = None
    word_type: Optional[str] = None
    difficulty_level: Optional[str] = 'medium'
    tags: Optional[str] = None


# Properties to receive on creation
class FlashcardCreate(FlashcardBase):
    document_id: Optional[int] = None

# Properties to receive on update
class FlashcardUpdate(FlashcardBase):
    front_text: Optional[str] = None
    back_text: Optional[str] = None
    difficulty_level: Optional[str] = None

# Properties shared by models stored in DB
class FlashcardInDBBase(FlashcardBase):
    id: int
    ease_factor: float
    interval: int
    repetitions: int
    next_review_date: Optional[datetime]
    times_reviewed: int
    times_correct: int
    last_review_quality: Optional[int]
    owner_id: int
    document_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# Properties to return to client
class Flashcard(FlashcardInDBBase):
    pass


# Properties stored in DB
class FlashcardInDB(FlashcardInDBBase):
    pass


# For SRS review responses
class FlashcardReview(BaseModel):
    quality: int  
    response_time: Optional[int] = None  
