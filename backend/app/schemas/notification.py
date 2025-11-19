# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    user_id: Optional[int] = None
    title: str
    body: str
    type: Optional[str] = None
    daily_plan_id: Optional[int] = None
    schedule_id: Optional[int] = None
    source_type: Optional[str] = "system"
    action_url: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    is_read: Optional[bool] = False
    created_at: datetime

    class Config:
        orm_mode = True
