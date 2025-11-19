# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int
    title: str
    body: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
