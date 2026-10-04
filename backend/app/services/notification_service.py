import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.models import Notification

class NotificationService:
    @staticmethod
    def create_notification(db: Session, employee_id: int, title: str, message: str) -> Notification:
        notification = Notification(
            employee_id=employee_id,
            title=title,
            message=message,
            is_read=False,
            created_at=datetime.datetime.utcnow()
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_user_notifications(db: Session, employee_id: int, limit: int = 50) -> List[Notification]:
        return db.query(Notification)\
            .filter(Notification.employee_id == employee_id)\
            .order_by(Notification.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, employee_id: int) -> bool:
        notification = db.query(Notification)\
            .filter(Notification.id == notification_id, Notification.employee_id == employee_id)\
            .first()
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(db: Session, employee_id: int) -> int:
        updated = db.query(Notification)\
            .filter(Notification.employee_id == employee_id, Notification.is_read == False)\
            .update({"is_read": True})
        db.commit()
        return updated
