from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.notification import Notification, NotificationCreate
from app.crud import crud_notification
from app.core.database import get_db

# Tạo router **không để prefix** ở đây
router = APIRouter()

# Lấy tất cả thông báo của một user
@router.get("/{user_id}", response_model=List[Notification])
def read_notifications(user_id: int, db: Session = Depends(get_db)):
    return crud_notification.get_notifications(db, user_id)

# Đánh dấu 1 thông báo đã đọc
@router.post("/{notification_id}/read", response_model=Notification)
def read_notification(notification_id: int, db: Session = Depends(get_db)):
    return crud_notification.mark_as_read(db, notification_id)

# Đánh dấu tất cả thông báo của user đã đọc
@router.post("/read-all/{user_id}")
def read_all_notifications(user_id: int, db: Session = Depends(get_db)):
    updated = crud_notification.mark_all_as_read(db, user_id)
    return {"updated_count": updated}

# Tạo thông báo mới
@router.post("/create", response_model=Notification)
def create_new_notification(notif: NotificationCreate, db: Session = Depends(get_db)):
    return crud_notification.create_notification(db, notif)
