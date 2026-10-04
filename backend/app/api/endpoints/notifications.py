from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee
from app.schemas.schemas import NotificationOut
from app.api.deps import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("", response_model=List[NotificationOut])
def get_notifications(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    return NotificationService.get_user_notifications(db, employee_id=current_user.employee_id)

@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    success = NotificationService.mark_as_read(db, notification_id, current_user.employee_id)
    return {"success": success}

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    count = NotificationService.mark_all_as_read(db, current_user.employee_id)
    return {"markedReadCount": count}
