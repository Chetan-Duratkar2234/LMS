from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee
from app.schemas.schemas import UtilizationReportItem, DepartmentReportItem, MonthlyReportItem
from app.api.deps import get_current_user
from app.services.reporting_service import ReportingService

router = APIRouter()

@router.get("/utilization", response_model=List[UtilizationReportItem])
def get_utilization_report(
    department: Optional[str] = Query(None),
    year: int = Query(2026),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return ReportingService.get_leave_utilization(db, department=department, year=year)

@router.get("/department", response_model=List[DepartmentReportItem])
def get_department_report(
    year: int = Query(2026),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return ReportingService.get_department_report(db, year=year)

@router.get("/monthly", response_model=List[MonthlyReportItem])
def get_monthly_report(
    year: int = Query(2026),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    return ReportingService.get_monthly_report(db, year=year)
