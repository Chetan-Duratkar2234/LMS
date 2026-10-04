from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from app.models.models import UserRole, LeaveStatus

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserOut"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Employee Schemas
class UserBase(BaseModel):
    employee_code: str
    name: str
    email: EmailStr
    role: str
    department: str
    designation: str
    manager_id: Optional[int] = None
    status: str = "ACTIVE"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None

class UserOut(UserBase):
    employee_id: int
    manager_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Leave Type Schemas
class LeaveTypeCreate(BaseModel):
    leave_code: str
    leave_name: str
    annual_limit: int
    carry_forward: bool = False
    requires_approval: bool = True

class LeaveTypeOut(LeaveTypeCreate):
    leave_type_id: int

    class Config:
        from_attributes = True

# Leave Balance Schemas
class LeaveBalanceOut(BaseModel):
    balance_id: int
    employee_id: int
    leave_type_id: int
    leave_type_name: str
    leave_code: str
    available_days: float
    used_days: float
    year: int

    class Config:
        from_attributes = True

# Standard Request/Response specs from User Requirements:
# POST /api/v1/leaves
# Request: { "leaveTypeId": 1, "startDate": "2026-09-20", "endDate": "2026-09-22", "reason": "Personal Work" }
# Response: { "requestId": 1001, "status": "PENDING" }

class LeaveApplyRequest(BaseModel):
    leave_type_id: int = Field(..., alias="leaveTypeId")
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    reason: str

    class Config:
        populate_by_name = True

class LeaveApplyResponse(BaseModel):
    request_id: int = Field(..., alias="requestId")
    status: str

    class Config:
        populate_by_name = True

class LeaveBalanceSummaryResponse(BaseModel):
    annual: float = 0.0
    sick: float = 0.0
    casual: float = 0.0
    detailed: List[LeaveBalanceOut] = []

class ApprovalActionRequest(BaseModel):
    comments: Optional[str] = "No comments provided"

class EscalateActionRequest(BaseModel):
    target_manager_id: Optional[int] = Field(None, alias="targetManagerId")
    comments: Optional[str] = "Escalated for review"

class DelegateActionRequest(BaseModel):
    delegate_to_id: int = Field(..., alias="delegateToId")
    comments: Optional[str] = "Delegated approval"

# Leave Request Detailed Schema
class ApprovalHistoryOut(BaseModel):
    history_id: int
    action: str
    action_by: str
    comments: Optional[str] = None
    action_date: datetime

    class Config:
        from_attributes = True

class LeaveRequestOut(BaseModel):
    request_id: int
    employee_id: int
    employee_code: str
    employee_name: str
    department: str
    leave_type_id: int
    leave_type_name: str
    leave_code: str
    start_date: date
    end_date: date
    days_count: float
    reason: str
    status: str
    delegated_to_id: Optional[int] = None
    delegated_to_name: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    approval_history: List[ApprovalHistoryOut] = []

    class Config:
        from_attributes = True

# Audit Log Schemas (matching sample audit log structure)
# { "event": "LEAVE_APPROVED", "performedBy": "MGR001", "requestId": "REQ1001", "timestamp": "2026-09-20T10:00:00Z" }
class AuditLogOut(BaseModel):
    event: str
    performed_by: str = Field(..., alias="performedBy")
    request_id: str = Field(..., alias="requestId")
    timestamp: datetime
    details: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

# Notification Schema
class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Report Schemas
class UtilizationReportItem(BaseModel):
    leave_type_name: str
    leave_code: str
    total_allocated: float
    total_used: float
    utilization_percentage: float

class DepartmentReportItem(BaseModel):
    department: str
    employee_count: int
    total_leaves_taken: float
    approved_requests: int
    pending_requests: int
    rejected_requests: int

class MonthlyReportItem(BaseModel):
    month_name: str
    year: int
    total_applications: int
    approved_count: int
    rejected_count: int
    cancelled_count: int
