from fastapi import APIRouter
from app.api.endpoints import auth, users, leaves, notifications, reports, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Module 1: User Management"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["Module 2 & 3: Leave & Approval Engine"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Module 4: Notification Service"])
api_router.include_router(reports.router, prefix="/reports", tags=["Module 5: Reporting Service"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Section 8: Audit & Logging"])
