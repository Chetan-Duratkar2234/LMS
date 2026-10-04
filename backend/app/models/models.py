import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    HR = "HR"
    ADMIN = "ADMIN"

class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. EMP1001, MGR001
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.EMPLOYEE.value, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")
    leave_balances = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", foreign_keys="[LeaveRequest.employee_id]", back_populates="employee")
    notifications = relationship("Notification", back_populates="employee", cascade="all, delete-orphan")

class LeaveType(Base):
    __tablename__ = "leave_types"

    leave_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    leave_code = Column(String(50), unique=True, nullable=False) # e.g. ANNUAL, SICK, CASUAL
    leave_name = Column(String(100), nullable=False)
    annual_limit = Column(Integer, nullable=False, default=15)
    carry_forward = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)

    # Relationships
    leave_balances = relationship("LeaveBalance", back_populates="leave_type")
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")

class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    balance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"), nullable=False)
    available_days = Column(Float, nullable=False, default=0.0)
    used_days = Column(Float, nullable=False, default=0.0)
    year = Column(Integer, nullable=False, default=2026)

    # Relationships
    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="leave_balances")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    request_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default=LeaveStatus.PENDING.value, nullable=False)
    delegated_to_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_requests")
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    delegated_to = relationship("Employee", foreign_keys=[delegated_to_id])
    approval_history = relationship("ApprovalHistory", back_populates="leave_request", cascade="all, delete-orphan")

class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("leave_requests.request_id"), nullable=False)
    action = Column(String(50), nullable=False) # APPLIED, APPROVED, REJECTED, CANCELLED, ESCALATED, DELEGATED
    action_by = Column(String(100), nullable=False) # employee_code or name
    comments = Column(Text, nullable=True)
    action_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    leave_request = relationship("LeaveRequest", back_populates="approval_history")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event = Column(String(100), nullable=False) # LEAVE_APPLIED, LEAVE_CANCELLED, LEAVE_APPROVED, LEAVE_REJECTED
    performed_by = Column(String(100), nullable=False) # e.g. MGR001
    request_id = Column(String(100), nullable=False) # e.g. REQ1001 or 1001
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text, nullable=True)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    employee = relationship("Employee", back_populates="notifications")
