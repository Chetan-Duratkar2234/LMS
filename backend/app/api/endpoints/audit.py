from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee
from app.schemas.schemas import AuditLogOut
from app.api.deps import get_current_user
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    requestId: Optional[str] = Query(None, alias="requestId"),
    event: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    logs = AuditService.get_audit_logs(db, request_id=requestId, event=event, limit=limit)
    out = []
    for log in logs:
        out.append(AuditLogOut(
            event=log.event,
            performed_by=log.performed_by,
            request_id=log.request_id,
            timestamp=log.timestamp,
            details=log.details
        ))
    return out
