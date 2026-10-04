from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee, LeaveType
from app.schemas.schemas import (
    LeaveApplyRequest, LeaveApplyResponse, LeaveBalanceSummaryResponse,
    ApprovalActionRequest, EscalateActionRequest, DelegateActionRequest,
    LeaveRequestOut, LeaveTypeOut
)
from app.api.deps import get_current_user
from app.services.leave_service import LeaveService
from app.services.approval_service import ApprovalService

router = APIRouter()

@router.get("/types", response_model=List[LeaveTypeOut])
def get_leave_types(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    return db.query(LeaveType).all()

@router.get("/balance", response_model=LeaveBalanceSummaryResponse)
def get_leave_balance(
    year: int = Query(2026),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return LeaveService.get_leave_balance(db, employee_id=current_user.employee_id, year=year)

@router.get("/all-balances")
def get_all_balances(
    year: int = Query(2026),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    from app.models.models import UserRole, LeaveBalance
    from fastapi import HTTPException
    if current_user.role not in [UserRole.HR.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    balances = db.query(LeaveBalance).filter(LeaveBalance.year == year).all()
    out = []
    for b in balances:
        out.append({
            "balance_id": b.balance_id,
            "employee_id": b.employee_id,
            "employee_name": b.employee.name if b.employee else "Unknown",
            "leave_type_name": b.leave_type.leave_name if b.leave_type else "Unknown",
            "available_days": b.available_days,
            "used_days": b.used_days
        })
    return out

from pydantic import BaseModel
class BalanceUpdate(BaseModel):
    available_days: float

@router.put("/balances/{balance_id}")
def update_balance(
    balance_id: int,
    data: BalanceUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    from app.models.models import UserRole, LeaveBalance
    from fastapi import HTTPException
    if current_user.role not in [UserRole.HR.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    b = db.query(LeaveBalance).filter(LeaveBalance.balance_id == balance_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Balance not found")
    
    b.available_days = data.available_days
    db.commit()
    db.refresh(b)
    return {"status": "success", "available_days": b.available_days}

@router.post("", response_model=LeaveApplyResponse, status_code=status.HTTP_201_CREATED)
def apply_leave(
    leave_in: LeaveApplyRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return LeaveService.apply_leave(
        db=db,
        employee_id=current_user.employee_id,
        leave_type_id=leave_in.leave_type_id,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        reason=leave_in.reason
    )

@router.get("", response_model=List[LeaveRequestOut])
def get_leave_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return LeaveService.get_user_leaves(db=db, current_user=current_user, status_filter=status_filter)

@router.post("/{request_id}/approve")
def approve_leave(
    request_id: int,
    action_in: Optional[ApprovalActionRequest] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    comments = action_in.comments if action_in and action_in.comments else "Approved"
    return ApprovalService.approve_leave(db, request_id, current_user, comments)

@router.post("/{request_id}/reject")
def reject_leave(
    request_id: int,
    action_in: Optional[ApprovalActionRequest] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    comments = action_in.comments if action_in and action_in.comments else "Rejected"
    return ApprovalService.reject_leave(db, request_id, current_user, comments)

@router.post("/{request_id}/cancel")
def cancel_leave(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    updated = LeaveService.cancel_leave(db, request_id, current_user)
    return {"requestId": updated.request_id, "status": updated.status}

@router.post("/{request_id}/escalate")
def escalate_leave(
    request_id: int,
    action_in: Optional[EscalateActionRequest] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    target_id = action_in.target_manager_id if action_in else None
    comments = action_in.comments if action_in and action_in.comments else "Escalated"
    return ApprovalService.escalate_leave(db, request_id, current_user, target_id, comments)

@router.post("/{request_id}/delegate")
def delegate_leave(
    request_id: int,
    action_in: DelegateActionRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return ApprovalService.delegate_approval(db, request_id, current_user, action_in.delegate_to_id, action_in.comments or "Delegated")
