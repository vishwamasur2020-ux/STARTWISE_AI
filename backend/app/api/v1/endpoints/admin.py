"""
STARTWISE AI — Admin API Endpoints (Stage 12)
All routes are protected by get_admin_user() dependency (RBAC).
Only ADMIN role can access. Normal users receive 403 Forbidden.

Routes:
  GET    /api/v1/admin/dashboard
  GET    /api/v1/admin/users
  GET    /api/v1/admin/users/{id}
  PATCH  /api/v1/admin/users/{id}/status
  PATCH  /api/v1/admin/users/{id}/role
  DELETE /api/v1/admin/users/{id}
  GET    /api/v1/admin/startups
  GET    /api/v1/admin/startups/{id}
  GET    /api/v1/admin/predictions
  GET    /api/v1/admin/franchises
  POST   /api/v1/admin/franchises
  GET    /api/v1/admin/franchises/{id}
  PUT    /api/v1/admin/franchises/{id}
  DELETE /api/v1/admin/franchises/{id}
  PATCH  /api/v1/admin/franchises/{id}/status
  GET    /api/v1/admin/marketing
  DELETE /api/v1/admin/marketing/{id}
  GET    /api/v1/admin/reports
  DELETE /api/v1/admin/reports/{id}
  GET    /api/v1/admin/ml
  GET    /api/v1/admin/audit-logs
  GET    /api/v1/admin/analytics
  GET    /api/v1/admin/settings
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_admin_user
from app.models.models import User
from app.services.admin_service import AdminService
from app.schemas.admin_schemas import (
    AdminDashboardStats,
    AdminUserListResponse, AdminUserDetail, AdminUserOut,
    UpdateUserStatusRequest, UpdateUserRoleRequest,
    AdminStartupListResponse, AdminStartupDetail,
    AdminPredictionListResponse,
    AdminFranchiseListResponse, AdminFranchiseOut,
    AdminFranchiseCreate, AdminFranchiseUpdate,
    ToggleFranchiseStatusRequest,
    AdminMarketingListResponse,
    AdminReportListResponse,
    AdminMLResponse,
    AdminAuditLogListResponse,
    AdminAnalyticsResponse,
    AdminSettingsResponse,
)
from app.schemas.schemas import MessageResponse

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


# ─── Require Admin dependency shortcut ──────────────────────────────────────
def require_admin(current_user: User = Depends(get_admin_user)) -> User:
    """Reusable dependency enforcing ADMIN role. Returns 403 for non-admins."""
    return current_user


# ─── Dashboard ───────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=AdminDashboardStats,
    summary="Admin Dashboard Statistics",
    description="Returns aggregated platform KPIs from the database. Admin only.",
)
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Return aggregated platform statistics for admin dashboard."""
    service = AdminService(db)
    return await service.get_dashboard_stats()


# ─── User Management ─────────────────────────────────────────────────────────

@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List All Users (Admin)",
)
async def admin_list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or ID"),
    role: Optional[str] = Query(None, description="Filter by role: user or admin"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_users(
        page=page, per_page=per_page,
        search=search, role=role,
        is_active=is_active, is_verified=is_verified,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetail,
    summary="Get User Detail (Admin)",
)
async def admin_get_user(
    user_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    result = await service.get_user_detail(user_id)
    await service.log_action(admin, "USER_VIEWED", "user", str(user_id), request)
    return result


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserOut,
    summary="Activate or Deactivate User (Admin)",
)
async def admin_update_user_status(
    user_id: UUID = Path(...),
    payload: UpdateUserStatusRequest = ...,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_user_status(user_id, payload.is_active, admin, request)


@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserOut,
    summary="Change User Role (Admin)",
)
async def admin_update_user_role(
    user_id: UUID = Path(...),
    payload: UpdateUserRoleRequest = ...,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_user_role(user_id, payload.role, admin, request)


@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    summary="Delete User (Admin)",
)
async def admin_delete_user(
    user_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    result = await service.delete_user(user_id, admin, request)
    return MessageResponse(message=result["message"], success=True)


# ─── Startup Management ───────────────────────────────────────────────────────

@router.get(
    "/startups",
    response_model=AdminStartupListResponse,
    summary="List All Startups (Admin)",
)
async def admin_list_startups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_startups(
        page=page, per_page=per_page,
        search=search, category=category, risk_level=risk_level,
    )


@router.get(
    "/startups/{startup_id}",
    response_model=AdminStartupDetail,
    summary="Get Startup Detail (Admin)",
)
async def admin_get_startup(
    startup_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_startup_detail(startup_id, admin, request)


# ─── Prediction Monitoring ────────────────────────────────────────────────────

@router.get(
    "/predictions",
    response_model=AdminPredictionListResponse,
    summary="List All Predictions (Admin)",
)
async def admin_list_predictions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_predictions(page=page, per_page=per_page, search=search)


# ─── Franchise Management ─────────────────────────────────────────────────────

@router.get(
    "/franchises",
    response_model=AdminFranchiseListResponse,
    summary="List All Franchises (Admin, incl. inactive)",
)
async def admin_list_franchises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    industry: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_franchises_admin(
        page=page, per_page=per_page,
        search=search, is_active=is_active, industry=industry,
    )


@router.post(
    "/franchises",
    response_model=AdminFranchiseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Franchise (Admin)",
)
async def admin_create_franchise(
    payload: AdminFranchiseCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_franchise_admin(payload, admin, request)


@router.get(
    "/franchises/{franchise_id}",
    response_model=AdminFranchiseOut,
    summary="Get Franchise (Admin)",
)
async def admin_get_franchise(
    franchise_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_franchise_admin(franchise_id)


@router.put(
    "/franchises/{franchise_id}",
    response_model=AdminFranchiseOut,
    summary="Update Franchise (Admin)",
)
async def admin_update_franchise(
    franchise_id: UUID = Path(...),
    payload: AdminFranchiseUpdate = ...,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_franchise_admin(franchise_id, payload, admin, request)


@router.delete(
    "/franchises/{franchise_id}",
    response_model=MessageResponse,
    summary="Delete Franchise (Admin)",
)
async def admin_delete_franchise(
    franchise_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    result = await service.delete_franchise_admin(franchise_id, admin, request)
    return MessageResponse(message=result["message"], success=True)


@router.patch(
    "/franchises/{franchise_id}/status",
    response_model=AdminFranchiseOut,
    summary="Toggle Franchise Active Status (Admin)",
)
async def admin_toggle_franchise_status(
    franchise_id: UUID = Path(...),
    payload: ToggleFranchiseStatusRequest = ...,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.toggle_franchise_status(franchise_id, payload.is_active, admin, request)


# ─── Marketing Management ─────────────────────────────────────────────────────

@router.get(
    "/marketing",
    response_model=AdminMarketingListResponse,
    summary="List Marketing Strategies (Admin)",
)
async def admin_list_marketing(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_marketing_admin(page=page, per_page=per_page, search=search)


@router.delete(
    "/marketing/{strategy_id}",
    response_model=MessageResponse,
    summary="Delete Marketing Strategy (Admin)",
)
async def admin_delete_marketing(
    strategy_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    result = await service.delete_marketing_admin(strategy_id, admin, request)
    return MessageResponse(message=result["message"], success=True)


# ─── Report Management ────────────────────────────────────────────────────────

@router.get(
    "/reports",
    response_model=AdminReportListResponse,
    summary="List All Reports (Admin)",
)
async def admin_list_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_reports_admin(page=page, per_page=per_page, search=search)


@router.delete(
    "/reports/{report_id}",
    response_model=MessageResponse,
    summary="Delete Report (Admin)",
)
async def admin_delete_report(
    report_id: UUID = Path(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    result = await service.delete_report_admin(report_id, admin, request)
    return MessageResponse(message=result["message"], success=True)


# ─── ML Monitoring ───────────────────────────────────────────────────────────

@router.get(
    "/ml",
    response_model=AdminMLResponse,
    summary="ML Model Monitoring (Admin)",
)
async def admin_ml_info(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_ml_info()


# ─── Audit Logs ──────────────────────────────────────────────────────────────

@router.get(
    "/audit-logs",
    response_model=AdminAuditLogListResponse,
    summary="Admin Audit Logs",
)
async def admin_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_audit_logs(
        page=page, per_page=per_page,
        action=action, resource=resource,
        start_date=start_date, end_date=end_date,
    )


# ─── Analytics ───────────────────────────────────────────────────────────────

@router.get(
    "/analytics",
    response_model=AdminAnalyticsResponse,
    summary="Platform Analytics (Admin)",
)
async def admin_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: str = Query("day", pattern="^(day|month)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_analytics(
        start_date=start_date, end_date=end_date, group_by=group_by,
    )


# ─── Settings ────────────────────────────────────────────────────────────────

@router.get(
    "/settings",
    response_model=AdminSettingsResponse,
    summary="Platform Settings Overview (Admin)",
)
async def admin_settings(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_settings()
