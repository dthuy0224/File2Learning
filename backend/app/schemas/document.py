from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# Shared properties
class DocumentBase(BaseModel):
    filename: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    difficulty_level: Optional[str] = 'medium'


# Properties to receive on creation
class DocumentCreate(DocumentBase):
    filename: str
    document_type: str
    

# Properties to receive on update
class DocumentUpdate(DocumentBase):
    title: Optional[str] = None
    summary: Optional[str] = None
    difficulty_level: Optional[str] = None


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
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        orm_mode = True


# Properties to return to client
class Document(DocumentInDBBase):
    pass


# Properties stored in DB
class DocumentInDB(DocumentInDBBase):
    pass
