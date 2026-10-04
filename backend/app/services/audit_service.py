import datetime
from sqlalchemy.orm import Session
from app.models.models import AuditLog

class AuditService:
    @staticmethod
    def log_event(db: Session, event: str, performed_by: str, request_id: str, details: str = None) -> AuditLog:
        audit_entry = AuditLog(
            event=event,
            performed_by=performed_by,
            request_id=f"REQ{request_id}" if not str(request_id).startswith("REQ") else str(request_id),
            timestamp=datetime.datetime.utcnow(),
            details=details
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    def get_audit_logs(db: Session, request_id: str = None, event: str = None, limit: int = 100):
        query = db.query(AuditLog)
        if request_id:
            req_str = f"REQ{request_id}" if not str(request_id).startswith("REQ") else str(request_id)
            query = query.filter(AuditLog.request_id == req_str)
        if event:
            query = query.filter(AuditLog.event == event)
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
