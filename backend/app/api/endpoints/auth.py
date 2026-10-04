from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee
from app.schemas.schemas import Token, LoginRequest, UserOut
from app.api.deps import verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.employee_id)})
    
    manager_name = user.manager.name if user.manager else None
    user_out = UserOut(
        employee_id=user.employee_id,
        employee_code=user.employee_code,
        name=user.name,
        email=user.email,
        role=user.role,
        department=user.department,
        designation=user.designation,
        manager_id=user.manager_id,
        manager_name=manager_name,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_out
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: Employee = Depends(get_current_user)):
    manager_name = current_user.manager.name if current_user.manager else None
    return UserOut(
        employee_id=current_user.employee_id,
        employee_code=current_user.employee_code,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        department=current_user.department,
        designation=current_user.designation,
        manager_id=current_user.manager_id,
        manager_name=manager_name,
        status=current_user.status,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
