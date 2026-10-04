import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import (
    Employee, LeaveType, LeaveBalance, LeaveRequest, ApprovalHistory, LeaveStatus, UserRole
)
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

class LeaveService:
    @staticmethod
    def calculate_days(start_date: datetime.date, end_date: datetime.date) -> float:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date cannot be prior to start date"
            )
        # Calculate inclusive days count
        delta = (end_date - start_date).days + 1
        return float(delta)

    @staticmethod
    def apply_leave(
        db: Session,
        employee_id: int,
        leave_type_id: int,
        start_date: datetime.date,
        end_date: datetime.date,
        reason: str
    ) -> Dict[str, Any]:
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == leave_type_id).first()
        if not leave_type:
            raise HTTPException(status_code=404, detail="Leave type not found")

        days_requested = LeaveService.calculate_days(start_date, end_date)

        # Check balance for current year
        current_year = datetime.datetime.utcnow().year
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.year == current_year
        ).first()

        if not balance:
            # Auto initialize balance if not present using annual_limit
            balance = LeaveBalance(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                available_days=float(leave_type.annual_limit),
                used_days=0.0,
                year=current_year
            )
            db.add(balance)
            db.commit()
            db.refresh(balance)

        if balance.available_days < days_requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {balance.available_days} days, Requested: {days_requested} days."
            )

        # Initial status: PENDING if approval required, else AUTO-APPROVED
        initial_status = LeaveStatus.PENDING.value if leave_type.requires_approval else LeaveStatus.APPROVED.value

        leave_req = LeaveRequest(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=initial_status,
            created_at=datetime.datetime.utcnow(),
            approved_at=datetime.datetime.utcnow() if initial_status == LeaveStatus.APPROVED.value else None
        )
        db.add(leave_req)
        db.commit()
        db.refresh(leave_req)

        # Record Approval History
        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="APPLIED",
            action_by=employee.employee_code,
            comments=f"Applied for {days_requested} day(s) of {leave_type.leave_name}",
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()

        # Audit Event: LEAVE_APPLIED
        AuditService.log_event(
            db=db,
            event="LEAVE_APPLIED",
            performed_by=employee.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Applied for {days_requested} days starting {start_date} to {end_date}"
        )

        # Notify Manager if exists
        if employee.manager_id:
            NotificationService.create_notification(
                db=db,
                employee_id=employee.manager_id,
                title="New Leave Request Pending",
                message=f"{employee.name} ({employee.employee_code}) applied for {leave_type.leave_name} from {start_date} to {end_date}."
            )

        return {
            "requestId": leave_req.request_id,
            "status": leave_req.status
        }

    @staticmethod
    def get_leave_balance(db: Session, employee_id: int, year: int = 2026) -> Dict[str, Any]:
        balances = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == year
        ).all()

        # Map to dict with default structure { "annual": X, "sick": Y, "casual": Z }
        summary = {"annual": 0.0, "sick": 0.0, "casual": 0.0}
        detailed_list = []

        for b in balances:
            lt = b.leave_type
            code_lower = lt.leave_code.lower() if lt else ""
            if "annual" in code_lower:
                summary["annual"] = b.available_days
            elif "sick" in code_lower:
                summary["sick"] = b.available_days
            elif "casual" in code_lower:
                summary["casual"] = b.available_days

            detailed_list.append({
                "balance_id": b.balance_id,
                "employee_id": b.employee_id,
                "leave_type_id": b.leave_type_id,
                "leave_type_name": lt.leave_name if lt else "Unknown",
                "leave_code": lt.leave_code if lt else "UNKNOWN",
                "available_days": b.available_days,
                "used_days": b.used_days,
                "year": b.year
            })

        summary["detailed"] = detailed_list
        return summary

    @staticmethod
    def cancel_leave(db: Session, request_id: int, current_user: Employee) -> LeaveRequest:
        leave_req = db.query(LeaveRequest).filter(LeaveRequest.request_id == request_id).first()
        if not leave_req:
            raise HTTPException(status_code=404, detail="Leave request not found")

        # Authorization: Only owner or Manager/HR/Admin can cancel
        if current_user.role == UserRole.EMPLOYEE.value and leave_req.employee_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="Unauthorized to cancel this leave request")

        if leave_req.status == LeaveStatus.CANCELLED.value:
            raise HTTPException(status_code=400, detail="Leave request is already cancelled")

        prev_status = leave_req.status
        leave_req.status = LeaveStatus.CANCELLED.value
        db.commit()

        # If it was previously APPROVED, refund days to balance
        if prev_status == LeaveStatus.APPROVED.value:
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
                db.commit()

        # Approval History
        history = ApprovalHistory(
            request_id=leave_req.request_id,
            action="CANCELLED",
            action_by=current_user.employee_code,
            comments="Leave request cancelled",
            action_date=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()

        # Audit Event: LEAVE_CANCELLED
        AuditService.log_event(
            db=db,
            event="LEAVE_CANCELLED",
            performed_by=current_user.employee_code,
            request_id=str(leave_req.request_id),
            details=f"Cancelled leave request REQ{leave_req.request_id}"
        )

        # Notify manager / employee
        if leave_req.employee.manager_id:
            NotificationService.create_notification(
                db=db,
                employee_id=leave_req.employee.manager_id,
                title="Leave Request Cancelled",
                message=f"{current_user.name} cancelled leave request REQ{leave_req.request_id}."
            )

        return leave_req

    @staticmethod
    def get_user_leaves(db: Session, current_user: Employee, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(LeaveRequest)

        if current_user.role == UserRole.EMPLOYEE.value:
            query = query.filter(LeaveRequest.employee_id == current_user.employee_id)
        elif current_user.role == UserRole.MANAGER.value:
            # Manager sees direct reports leaves OR their own OR delegated leaves
            direct_report_ids = [e.employee_id for e in current_user.direct_reports]
            direct_report_ids.append(current_user.employee_id)
            query = query.filter(
                (LeaveRequest.employee_id.in_(direct_report_ids)) |
                (LeaveRequest.delegated_to_id == current_user.employee_id)
            )

        if status_filter:
            query = query.filter(LeaveRequest.status == status_filter.upper())

        requests = query.order_by(LeaveRequest.created_at.desc()).all()

        result = []
        for req in requests:
            days = LeaveService.calculate_days(req.start_date, req.end_date)
            history = db.query(ApprovalHistory).filter(ApprovalHistory.request_id == req.request_id).order_by(ApprovalHistory.action_date.asc()).all()
            
            result.append({
                "request_id": req.request_id,
                "employee_id": req.employee_id,
                "employee_code": req.employee.employee_code if req.employee else "",
                "employee_name": req.employee.name if req.employee else "Unknown",
                "department": req.employee.department if req.employee else "N/A",
                "leave_type_id": req.leave_type_id,
                "leave_type_name": req.leave_type.leave_name if req.leave_type else "N/A",
                "leave_code": req.leave_type.leave_code if req.leave_type else "N/A",
                "start_date": req.start_date,
                "end_date": req.end_date,
                "days_count": days,
                "reason": req.reason,
                "status": req.status,
                "delegated_to_id": req.delegated_to_id,
                "delegated_to_name": req.delegated_to.name if req.delegated_to else None,
                "created_at": req.created_at,
                "approved_at": req.approved_at,
                "approval_history": history
            })
        return result
