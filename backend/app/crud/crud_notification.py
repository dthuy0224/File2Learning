# app/crud/crud_notification.py
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

def get_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def mark_as_read(db: Session, notification_id: int):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif

def mark_all_as_read(db: Session, user_id: int):
    updated = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return updated

def create_notification(db: Session, notif: NotificationCreate):
    db_notif = Notification(**notif.dict())
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif
