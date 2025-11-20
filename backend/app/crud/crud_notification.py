# app/crud/crud_notification.py
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from typing import Optional, List


def get_notifications(db: Session, user_id: int):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_as_read(db: Session, notification_id: int):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif


def mark_all_as_read(db: Session, user_id: int):
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return updated


def create_notification(db: Session, notif: NotificationCreate):
    db_notif = Notification(**notif.dict())
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif


# 🆕 THÊM: Hàm tạo notification với tất cả fields
def create_notification_full(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    type: str = "system",
    source_type: str = "system",
    daily_plan_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    action_url: Optional[str] = None,
):
    """Create a notification with full details"""
    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        type=type,
        source_type=source_type,
        daily_plan_id=daily_plan_id,
        schedule_id=schedule_id,
        action_url=action_url,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


# 🆕 THÊM: Lấy notifications theo plan
def get_plan_notifications(db: Session, daily_plan_id: int) -> List[Notification]:
    """Get all notifications for a specific plan"""
    return (
        db.query(Notification)
        .filter(Notification.daily_plan_id == daily_plan_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


# 🆕 THÊM: Lấy notifications theo schedule
def get_schedule_notifications(db: Session, schedule_id: int) -> List[Notification]:
    """Get all notifications for a specific schedule"""
    return (
        db.query(Notification)
        .filter(Notification.schedule_id == schedule_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
