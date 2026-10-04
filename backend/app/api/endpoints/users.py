from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee, UserRole, LeaveType, LeaveBalance
from app.schemas.schemas import UserOut, UserCreate, UserUpdate
from app.api.deps import get_current_user, get_password_hash

router = APIRouter()

@router.get("", response_model=List[UserOut])
def list_users(
    role: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    query = db.query(Employee)
    if role:
        query = query.filter(Employee.role == role.upper())
    if department:
        query = query.filter(Employee.department == department)

    users = query.all()
    out = []
    for u in users:
        out.append(UserOut(
            employee_id=u.employee_id,
            employee_code=u.employee_code,
            name=u.name,
            email=u.email,
            role=u.role,
            department=u.department,
            designation=u.designation,
            manager_id=u.manager_id,
            manager_name=u.manager.name if u.manager else None,
            status=u.status,
            created_at=u.created_at,
            updated_at=u.updated_at
        ))
    return out

@router.get("/managers", response_model=List[UserOut])
def list_managers(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    managers = db.query(Employee).filter(Employee.role.in_([UserRole.MANAGER.value, UserRole.HR.value, UserRole.ADMIN.value])).all()
    out = []
    for u in managers:
        out.append(UserOut(
            employee_id=u.employee_id,
            employee_code=u.employee_code,
            name=u.name,
            email=u.email,
            role=u.role,
            department=u.department,
            designation=u.designation,
            manager_id=u.manager_id,
            manager_name=u.manager.name if u.manager else None,
            status=u.status,
            created_at=u.created_at,
            updated_at=u.updated_at
        ))
    return out

@router.post("", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN.value, UserRole.HR.value]:
        raise HTTPException(status_code=403, detail="Only HR or Admin can create users")

    existing = db.query(Employee).filter((Employee.email == user_in.email) | (Employee.employee_code == user_in.employee_code)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or employee code already exists")

    new_emp = Employee(
        employee_code=user_in.employee_code,
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role.upper(),
        department=user_in.department,
        designation=user_in.designation,
        manager_id=user_in.manager_id,
        status=user_in.status
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    # Initialize default leave balances for current year
    leave_types = db.query(LeaveType).all()
    for lt in leave_types:
        bal = LeaveBalance(
            employee_id=new_emp.employee_id,
            leave_type_id=lt.leave_type_id,
            available_days=float(lt.annual_limit),
            used_days=0.0,
            year=2026
        )
        db.add(bal)
    db.commit()

    return UserOut(
        employee_id=new_emp.employee_id,
        employee_code=new_emp.employee_code,
        name=new_emp.name,
        email=new_emp.email,
        role=new_emp.role,
        department=new_emp.department,
        designation=new_emp.designation,
        manager_id=new_emp.manager_id,
        manager_name=new_emp.manager.name if new_emp.manager else None,
        status=new_emp.status,
        created_at=new_emp.created_at,
        updated_at=new_emp.updated_at
    )

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    user = db.query(Employee).filter(Employee.employee_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role not in [UserRole.ADMIN.value, UserRole.HR.value] and current_user.employee_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this user")

    update_data = user_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            if field == "role":
                setattr(user, field, val.upper())
            else:
                setattr(user, field, val)

    db.commit()
    db.refresh(user)

    return UserOut(
        employee_id=user.employee_id,
        employee_code=user.employee_code,
        name=user.name,
        email=user.email,
        role=user.role,
        department=user.department,
        designation=user.designation,
        manager_id=user.manager_id,
        manager_name=user.manager.name if user.manager else None,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
