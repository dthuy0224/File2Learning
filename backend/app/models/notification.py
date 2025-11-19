from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)

    # Thêm trường này để phân loại (reminder, achievement, system)
    type = Column(String, default="system")

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
