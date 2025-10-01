from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None  

class ChatResponse(BaseModel):
    answer: str
    document_id: int
    model_used: str
    conversation_id: Optional[str] = None 
