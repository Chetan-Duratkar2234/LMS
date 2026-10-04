import datetime

from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app.models.models import (
    Employee,
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    ApprovalHistory,
    AuditLog,
    Notification,
    UserRole,
    LeaveStatus,
)
from app.api.deps import get_password_hash


def get_or_create_leave_type(
    db: Session,
    leave_code: str,
    leave_name: str,
    annual_limit: int,
    carry_forward: bool,
    requires_approval: bool,
):
    """Get an existing leave type or create it."""

    leave_type = (
        db.query(LeaveType)
        .filter(LeaveType.leave_code == leave_code)
        .first()
    )

    if leave_type:
        return leave_type

    leave_type = LeaveType(
        leave_code=leave_code,
        leave_name=leave_name,
        annual_limit=annual_limit,
        carry_forward=carry_forward,
        requires_approval=requires_approval,
    )

    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)

    return leave_type


def get_or_create_employee(
    db: Session,
    employee_code: str,
    name: str,
    email: str,
    hashed_password: str,
    role: str,
    department: str,
    designation: str,
    status: str = "ACTIVE",
    manager_id=None,
):
    """Get an existing employee or create it."""

    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if employee:
        return employee

    employee = Employee(
        employee_code=employee_code,
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        department=department,
        designation=designation,
        status=status,
        manager_id=manager_id,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_or_create_balance(
    db: Session,
    employee_id: int,
    leave_type_id: int,
    year: int,
    available_days: float,
    used_days: float,
):
    """Create leave balance if it doesn't already exist."""

    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.year == year,
        )
        .first()
    )

    if balance:
        return balance

    balance = LeaveBalance(
        employee_id=employee_id,
        leave_type_id=leave_type_id,
        available_days=available_days,
        used_days=used_days,
        year=year,
    )

    db.add(balance)
    db.commit()
    db.refresh(balance)

    return balance


def seed_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Checking LMS database...")

        # ==========================================================
        # 1. LEAVE TYPES
        # ==========================================================

        print("Checking leave types...")

        annual_type = get_or_create_leave_type(
            db=db,
            leave_code="ANNUAL",
            leave_name="Annual Leave",
            annual_limit=15,
            carry_forward=True,
            requires_approval=True,
        )

        sick_type = get_or_create_leave_type(
            db=db,
            leave_code="SICK",
            leave_name="Sick Leave",
            annual_limit=8,
            carry_forward=False,
            requires_approval=True,
        )

        casual_type = get_or_create_leave_type(
            db=db,
            leave_code="CASUAL",
            leave_name="Casual Leave",
            annual_limit=6,
            carry_forward=False,
            requires_approval=True,
        )

        # ==========================================================
        # 2. PASSWORD
        # ==========================================================

        hashed_pwd = get_password_hash("password123")

        # ==========================================================
        # 3. USERS
        # ==========================================================

        print("Checking demo users...")

        # Admin
        admin_user = get_or_create_employee(
            db=db,
            employee_code="ADM001",
            name="Admin User",
            email="admin@lms.com",
            hashed_password=hashed_pwd,
            role=UserRole.ADMIN.value,
            department="Executive",
            designation="System Administrator",
            status="ACTIVE",
        )

        # HR
        hr_user = get_or_create_employee(
            db=db,
            employee_code="HR001",
            name="Sarah HR Lead",
            email="hr@lms.com",
            hashed_password=hashed_pwd,
            role=UserRole.HR.value,
            department="Human Resources",
            designation="HR Director",
            status="ACTIVE",
        )

        # Manager
        mgr_user = get_or_create_employee(
            db=db,
            employee_code="MGR001",
            name="Alex Manager",
            email="manager@lms.com",
            hashed_password=hashed_pwd,
            role=UserRole.MANAGER.value,
            department="Engineering",
            designation="Engineering Director",
            status="ACTIVE",
        )

        # Employee 1
        emp_user = get_or_create_employee(
            db=db,
            employee_code="EMP1001",
            name="John Doe",
            email="employee@lms.com",
            hashed_password=hashed_pwd,
            role=UserRole.EMPLOYEE.value,
            department="Engineering",
            designation="Senior Software Engineer",
            status="ACTIVE",
            manager_id=mgr_user.employee_id,
        )

        # Employee 2
        emp_user2 = get_or_create_employee(
            db=db,
            employee_code="EMP1002",
            name="Jane Smith",
            email="jane@lms.com",
            hashed_password=hashed_pwd,
            role=UserRole.EMPLOYEE.value,
            department="Engineering",
            designation="UI/UX Lead",
            status="ACTIVE",
            manager_id=mgr_user.employee_id,
        )

        # ==========================================================
        # 4. LEAVE BALANCES FOR 2026
        # ==========================================================

        print("Checking leave balances...")

        users_list = [
            admin_user,
            hr_user,
            mgr_user,
            emp_user,
            emp_user2,
        ]

        for user in users_list:

            get_or_create_balance(
                db=db,
                employee_id=user.employee_id,
                leave_type_id=annual_type.leave_type_id,
                available_days=15.0,
                used_days=0.0,
                year=2026,
            )

            get_or_create_balance(
                db=db,
                employee_id=user.employee_id,
                leave_type_id=sick_type.leave_type_id,
                available_days=8.0,
                used_days=0.0,
                year=2026,
            )

            get_or_create_balance(
                db=db,
                employee_id=user.employee_id,
                leave_type_id=casual_type.leave_type_id,
                available_days=6.0,
                used_days=0.0,
                year=2026,
            )

        # ==========================================================
        # 5. SAMPLE LEAVE REQUEST REQ1001
        # ==========================================================

        print("Checking sample leave request...")

        req1 = (
            db.query(LeaveRequest)
            .filter(LeaveRequest.request_id == 1001)
            .first()
        )

        if not req1:

            req1 = LeaveRequest(
                request_id=1001,
                employee_id=emp_user.employee_id,
                leave_type_id=annual_type.leave_type_id,
                start_date=datetime.date(2026, 9, 20),
                end_date=datetime.date(2026, 9, 22),
                reason="Personal Work",
                status=LeaveStatus.APPROVED.value,
                created_at=datetime.datetime(
                    2026, 9, 19, 9, 0, 0
                ),
                approved_at=datetime.datetime(
                    2026, 9, 20, 10, 0, 0
                ),
            )

            db.add(req1)
            db.commit()
            db.refresh(req1)

        # ==========================================================
        # 6. UPDATE EMPLOYEE LEAVE BALANCE FOR REQ1001
        # ==========================================================

        emp_ann_bal = (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == emp_user.employee_id,
                LeaveBalance.leave_type_id == annual_type.leave_type_id,
                LeaveBalance.year == 2026,
            )
            .first()
        )

        if emp_ann_bal:

            emp_ann_bal.available_days = 12.0
            emp_ann_bal.used_days = 3.0

            db.commit()

        # ==========================================================
        # 7. APPROVAL HISTORY
        # ==========================================================

        print("Checking approval history...")

        existing_history = (
            db.query(ApprovalHistory)
            .filter(ApprovalHistory.request_id == 1001)
            .count()
        )

        if existing_history == 0:

            h1 = ApprovalHistory(
                request_id=1001,
                action="APPLIED",
                action_by="EMP1001",
                comments="Personal Work",
                action_date=datetime.datetime(
                    2026, 9, 19, 9, 0, 0
                ),
            )

            h2 = ApprovalHistory(
                request_id=1001,
                action="APPROVED",
                action_by="MGR001",
                comments="Approved by Manager",
                action_date=datetime.datetime(
                    2026, 9, 20, 10, 0, 0
                ),
            )

            db.add_all([h1, h2])
            db.commit()

        # ==========================================================
        # 8. AUDIT LOGS
        # ==========================================================

        print("Checking audit logs...")

        existing_audit = (
            db.query(AuditLog)
            .filter(AuditLog.request_id == "REQ1001")
            .count()
        )

        if existing_audit == 0:

            audit1 = AuditLog(
                event="LEAVE_APPLIED",
                performed_by="EMP1001",
                request_id="REQ1001",
                timestamp=datetime.datetime(
                    2026, 9, 19, 9, 0, 0
                ),
                details="Applied for Annual Leave (3 days)",
            )

            audit2 = AuditLog(
                event="LEAVE_APPROVED",
                performed_by="MGR001",
                request_id="REQ1001",
                timestamp=datetime.datetime(
                    2026, 9, 20, 10, 0, 0
                ),
                details="Approved leave request REQ1001",
            )

            db.add_all([audit1, audit2])
            db.commit()

        # ==========================================================
        # 9. NOTIFICATIONS
        # ==========================================================

        print("Checking notifications...")

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.employee_id == emp_user.employee_id,
                Notification.title == "Leave Approved",
            )
            .first()
        )

        if not existing_notification:

            n1 = Notification(
                employee_id=emp_user.employee_id,
                title="Leave Approved",
                message=(
                    "Your Annual Leave request REQ1001 "
                    "from 2026-09-20 to 2026-09-22 "
                    "has been approved by MGR001."
                ),
                is_read=False,
                created_at=datetime.datetime(
                    2026, 9, 20, 10, 0, 0
                ),
            )

            db.add(n1)
            db.commit()

        # ==========================================================
        # DONE
        # ==========================================================

        print("")
        print("==========================================")
        print("LMS DATABASE SEEDING COMPLETE")
        print("==========================================")
        print("Demo users:")
        print("  Admin:    admin@lms.com")
        print("  HR:       hr@lms.com")
        print("  Manager:  manager@lms.com")
        print("  Employee: employee@lms.com")
        print("  Employee: jane@lms.com")
        print("")
        print("Demo password:")
        print("  password123")
        print("")
        print("Sample request:")
        print("  REQ1001")
        print("==========================================")

    except Exception as e:

        db.rollback()

        print("")
        print("==========================================")
        print("ERROR SEEDING DATABASE")
        print("==========================================")
        print(e)
        print("==========================================")

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
