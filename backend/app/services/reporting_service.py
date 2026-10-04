from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Employee, LeaveType, LeaveBalance, LeaveRequest, LeaveStatus

class ReportingService:
    @staticmethod
    def get_leave_utilization(db: Session, department: str = None, year: int = 2026) -> List[Dict[str, Any]]:
        query = db.query(
            LeaveType.leave_name,
            LeaveType.leave_code,
            func.sum(LeaveBalance.available_days + LeaveBalance.used_days).label("total_allocated"),
            func.sum(LeaveBalance.used_days).label("total_used")
        ).join(LeaveBalance, LeaveType.leave_type_id == LeaveBalance.leave_type_id)

        if department:
            query = query.join(Employee, Employee.employee_id == LeaveBalance.employee_id)\
                .filter(Employee.department == department)

        results = query.filter(LeaveBalance.year == year)\
            .group_by(LeaveType.leave_type_id, LeaveType.leave_name, LeaveType.leave_code)\
            .all()

        utilization = []
        for name, code, allocated, used in results:
            alloc_val = float(allocated or 0.0)
            used_val = float(used or 0.0)
            pct = round((used_val / alloc_val * 100), 2) if alloc_val > 0 else 0.0
            utilization.append({
                "leave_type_name": name,
                "leave_code": code,
                "total_allocated": alloc_val,
                "total_used": used_val,
                "utilization_percentage": pct
            })

        return utilization

    @staticmethod
    def get_department_report(db: Session, year: int = 2026) -> List[Dict[str, Any]]:
        departments = db.query(Employee.department).distinct().all()
        dept_names = [d[0] for d in departments if d[0]]

        report = []
        for dept in dept_names:
            emp_count = db.query(func.count(Employee.employee_id)).filter(
                Employee.department == dept,
                Employee.status == "ACTIVE"
            ).scalar() or 0

            leaves_taken = db.query(func.sum(LeaveBalance.used_days))\
                .join(Employee, Employee.employee_id == LeaveBalance.employee_id)\
                .filter(Employee.department == dept, LeaveBalance.year == year)\
                .scalar() or 0.0

            approved = db.query(func.count(LeaveRequest.request_id))\
                .join(Employee, Employee.employee_id == LeaveRequest.employee_id)\
                .filter(Employee.department == dept, LeaveRequest.status == LeaveStatus.APPROVED.value)\
                .scalar() or 0

            pending = db.query(func.count(LeaveRequest.request_id))\
                .join(Employee, Employee.employee_id == LeaveRequest.employee_id)\
                .filter(Employee.department == dept, LeaveRequest.status == LeaveStatus.PENDING.value)\
                .scalar() or 0

            rejected = db.query(func.count(LeaveRequest.request_id))\
                .join(Employee, Employee.employee_id == LeaveRequest.employee_id)\
                .filter(Employee.department == dept, LeaveRequest.status == LeaveStatus.REJECTED.value)\
                .scalar() or 0

            report.append({
                "department": dept,
                "employee_count": emp_count,
                "total_leaves_taken": float(leaves_taken),
                "approved_requests": approved,
                "pending_requests": pending,
                "rejected_requests": rejected
            })

        return report

    @staticmethod
    def get_monthly_report(db: Session, year: int = 2026) -> List[Dict[str, Any]]:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        report = []

        all_requests = db.query(LeaveRequest).all()

        for m_idx, m_name in enumerate(months, start=1):
            m_reqs = [
                r for r in all_requests 
                if r.created_at and r.created_at.year == year and r.created_at.month == m_idx
            ]
            total_app = len(m_reqs)
            approved = sum(1 for r in m_reqs if r.status == LeaveStatus.APPROVED.value)
            rejected = sum(1 for r in m_reqs if r.status == LeaveStatus.REJECTED.value)
            cancelled = sum(1 for r in m_reqs if r.status == LeaveStatus.CANCELLED.value)

            report.append({
                "month_name": m_name,
                "year": year,
                "total_applications": total_app,
                "approved_count": approved,
                "rejected_count": rejected,
                "cancelled_count": cancelled
            })

        return report
