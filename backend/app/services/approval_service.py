import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import (
    Employee, LeaveRequest, LeaveBalance, ApprovalHistory, LeaveStatus, UserRole
)
from app.services.leave_service import LeaveService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

class ApprovalService:
    @staticmethod
    def _get_request_and_authorize(db: Session, request_id: int, current_user: Employee) -> LeaveRequest:
        leave_req = db.query(LeaveRequest).filter(LeaveRequest.request_id == request_id).first()
        if not leave_req:
            raise HTTPException(status_code=404, detail="Leave request not found")

        # Allow Manager, HR, Admin or Delegated Employee to approve/reject
        is_manager_or_higher = current_user.role in [UserRole.MANAGER.value, UserRole.HR.value, UserRole.ADMIN.value]
        is_delegate = leave_req.delegated_to_id == current_user.employee_id
        is_direct_manager = leave_req.employee and leave_req.employee.manager_id == current_user.employee_id

        if not (is_manager_or_higher or is_delegate or is_direct_manager):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to process this leave request."
            )

        return leave_req

    @staticmethod
    def approve_leave(db: Session, request_id: int, current_user: Employee, comments: str = "Approved") -> Dict[str, Any]:
        leave_req = ApprovalService._get_request_and_authorize(db, request_id, current_user)

        if leave_req.status == LeaveStatus.APPROVED.value:
            raise HTTPException(status_code=400, detail="Leave request is already approved")

        days = LeaveService.calculate_days(leave_req.start_date, leave_req.end_date)
        current_year = datetime.datetime.utcnow().year

        # Deduct balance
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == leave_req.employee_id,
            LeaveBalance.leave_type_id == leave_req.leave_type_id,
            LeaveBalance.year == current_year
        ).first()

        if balance:
            if balance.available_days < days:
                raise HTTPException(status_code=400, detail=f"Insufficient balance to approve. Available: {balance.available_days}")
            balance.available_days -= days
            balance.used_days += days

        leave_req.status = LeaveStatus.APPROVED.value
        leave_req.approved_at = datetime.datetime.utcnow()

        # Approval History
        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="APPROVED",
            action_by=current_user.employee_code,
            comments=comments,
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()

        # Sample Audit Log payload structure matched:
        # { "event": "LEAVE_APPROVED", "performedBy": "MGR001", "requestId": "REQ1001", "timestamp": "2026-09-20T10:00:00Z" }
        AuditService.log_event(
            db=db,
            event="LEAVE_APPROVED",
            performed_by=current_user.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Approved leave for employee {leave_req.employee.employee_code if leave_req.employee else leave_req.employee_id}. Comments: {comments}"
        )

        # Notify Employee
        NotificationService.create_notification(
            db=db,
            employee_id=leave_req.employee_id,
            title="Leave Request Approved",
            message=f"Your leave request REQ{leave_req.request_id} ({leave_req.leave_type.leave_name}) from {leave_req.start_date} to {leave_req.end_date} has been approved by {current_user.name}."
        )

        return {"requestId": leave_req.request_id, "status": "APPROVED"}

    @staticmethod
    def reject_leave(db: Session, request_id: int, current_user: Employee, comments: str = "Rejected") -> Dict[str, Any]:
        leave_req = ApprovalService._get_request_and_authorize(db, request_id, current_user)

        if leave_req.status == LeaveStatus.REJECTED.value:
            raise HTTPException(status_code=400, detail="Leave request is already rejected")

        # If it was previously approved, restore balance
        if leave_req.status == LeaveStatus.APPROVED.value:
            days = LeaveService.calculate_days(leave_req.start_date, leave_req.end_date)
            current_year = datetime.datetime.utcnow().year
            balance = db.query(LeaveBalance).filter(
                LeaveBalance.employee_id == leave_req.employee_id,
                LeaveBalance.leave_type_id == leave_req.leave_type_id,
                LeaveBalance.year == current_year
            ).first()
            if balance:
                balance.available_days += days
                balance.used_days = max(0.0, balance.used_days - days)

        leave_req.status = LeaveStatus.REJECTED.value

        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="REJECTED",
            action_by=current_user.employee_code,
            comments=comments,
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()

        # Audit Event: LEAVE_REJECTED
        AuditService.log_event(
            db=db,
            event="LEAVE_REJECTED",
            performed_by=current_user.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Rejected leave request REQ{leave_req.request_id}. Comments: {comments}"
        )

        # Notify Employee
        NotificationService.create_notification(
            db=db,
            employee_id=leave_req.employee_id,
            title="Leave Request Rejected",
            message=f"Your leave request REQ{leave_req.request_id} has been rejected by {current_user.name}. Reason: {comments}"
        )

        return {"requestId": leave_req.request_id, "status": "REJECTED"}

    @staticmethod
    def escalate_leave(db: Session, request_id: int, current_user: Employee, target_manager_id: Optional[int] = None, comments: str = "Escalated") -> Dict[str, Any]:
        leave_req = db.query(LeaveRequest).filter(LeaveRequest.request_id == request_id).first()
        if not leave_req:
            raise HTTPException(status_code=404, detail="Leave request not found")

        leave_req.status = LeaveStatus.ESCALATED.value

        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="ESCALATED",
            action_by=current_user.employee_code,
            comments=comments,
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)

        if target_manager_id:
            leave_req.delegated_to_id = target_manager_id

        db.commit()

        AuditService.log_event(
            db=db,
            event="LEAVE_ESCALATED",
            performed_by=current_user.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Escalated leave request REQ{leave_req.request_id}. Comments: {comments}"
        )

        # Notify HR / Target Manager
        if target_manager_id:
            NotificationService.create_notification(
                db=db,
                employee_id=target_manager_id,
                title="Escalated Leave Request",
                message=f"Leave request REQ{leave_req.request_id} has been escalated to you by {current_user.name}."
            )

        return {"requestId": leave_req.request_id, "status": "ESCALATED"}

    @staticmethod
    def delegate_approval(db: Session, request_id: int, current_user: Employee, delegate_to_id: int, comments: str = "Delegated") -> Dict[str, Any]:
        leave_req = ApprovalService._get_request_and_authorize(db, request_id, current_user)

        delegatee = db.query(Employee).filter(Employee.employee_id == delegate_to_id).first()
        if not delegatee:
            raise HTTPException(status_code=404, detail="Delegate employee not found")

        leave_req.delegated_to_id = delegate_to_id

        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="DELEGATED",
            action_by=current_user.employee_code,
            comments=f"Delegated to {delegatee.name} ({delegatee.employee_code}). {comments}",
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()

        AuditService.log_event(
            db=db,
            event="LEAVE_DELEGATED",
            performed_by=current_user.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Delegated approval for REQ{leave_req.request_id} to {delegatee.employee_code}"
        )

        NotificationService.create_notification(
            db=db,
            employee_id=delegate_to_id,
            title="Delegated Leave Approval",
            message=f"{current_user.name} delegated approval of request REQ{leave_req.request_id} to you."
        )

        return {"requestId": leave_req.request_id, "status": leave_req.status, "delegatedTo": delegatee.name}
