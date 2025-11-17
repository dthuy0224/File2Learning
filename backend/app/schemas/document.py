from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# Shared properties
class DocumentBase(BaseModel):
    filename: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    difficulty_level: Optional[str] = 'medium'
    key_vocabulary: Optional[List[Dict[str, str]]] = None
    summary_status: Optional[str] = None
    summary_error: Optional[str] = None
    summary_generated_at: Optional[datetime] = None
    vocab_status: Optional[str] = None
    vocab_error: Optional[str] = None
    vocab_generated_at: Optional[datetime] = None
    quiz_status: Optional[str] = None
    quiz_error: Optional[str] = None
    quiz_generated_at: Optional[datetime] = None


# Properties to receive on creation
class DocumentCreate(DocumentBase):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    document_type: str
    word_count: Optional[int] = 0
    processing_status: str = 'pending'
    content: Optional[str] = None
    

# Properties to receive on update
class DocumentUpdate(DocumentBase):
    title: Optional[str] = None
    summary: Optional[str] = None
    difficulty_level: Optional[str] = None
    content: Optional[str] = None
    word_count: Optional[int] = None
    processing_status: Optional[str] = None
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    content_quality: Optional[str] = None
    quality_score: Optional[int] = None
    language_detected: Optional[str] = None
    encoding_issues: Optional[int] = None
    summary_status: Optional[str] = None
    summary_error: Optional[str] = None
    summary_generated_at: Optional[datetime] = None
    vocab_status: Optional[str] = None
    vocab_error: Optional[str] = None
    vocab_generated_at: Optional[datetime] = None
    quiz_status: Optional[str] = None
    quiz_error: Optional[str] = None
    quiz_generated_at: Optional[datetime] = None


# Properties shared by models stored in DB
class DocumentInDBBase(DocumentBase):
    id: int
    original_filename: str
    file_path: str
    file_size: Optional[int]
    content: Optional[str]
    summary: Optional[str]
    word_count: int
    owner_id: int
    processing_status: str
    processing_error: Optional[str]
    content_quality: Optional[str]
    quality_score: Optional[int]
    language_detected: Optional[str]
    encoding_issues: Optional[int]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Properties to return to client
class Document(DocumentInDBBase):
    pass

# Properties stored in DB
class DocumentInDB(DocumentInDBBase):
    pass


# Properties for topic-based document creation
class DocumentCreateFromTopic(BaseModel):
    topic: str = Field(..., min_length=3, max_length=150, description="The topic that the user wants AI to generate content for")