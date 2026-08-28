"""
STARTWISE AI — Admin Service (Stage 12)
Business logic layer for all admin operations.
Router → Service → Repository → SQLAlchemy → PostgreSQL
"""

from datetime import datetime, timezone
from math import ceil
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Franchise, MarketingStrategy, Report, AuditLog
from app.repositories.admin_repository import AdminRepository
from app.repositories.franchise_repository import FranchiseRepository
from app.core.exceptions import (
    NotFoundException, ForbiddenException, BadRequestException, ConflictException
)
from app.core.model_manager import get_model_manager
from app.core.logging import get_logger
from app.schemas.admin_schemas import (
    AdminDashboardStats, UserStats, StartupStats, PredictionStats, ReportStats, FranchiseStats,
    AdminUserOut, AdminUserListResponse, AdminUserDetail,
    AdminStartupOut, AdminStartupListResponse, AdminStartupDetail,
    AdminPredictionOut, AdminPredictionListResponse,
    AdminFranchiseOut, AdminFranchiseListResponse, AdminFranchiseCreate, AdminFranchiseUpdate,
    AdminMarketingOut, AdminMarketingListResponse,
    AdminReportOut, AdminReportListResponse,
    AdminMLResponse, ModelInfo, ServiceHealthItem,
    AdminAuditLogOut, AdminAuditLogListResponse,
    AdminAnalyticsResponse, TimeSeriesPoint, DistributionItem,
    AdminSettingsResponse,
)

logger = get_logger(__name__)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.franchise_repo = FranchiseRepository(db)

    # ── Audit Logging Helper ─────────────────────────────────────────────────

    async def log_action(
        self,
        admin: User,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        ip = None
        ua = None
        if request:
            ip = request.client.host if request.client else None
            ua = request.headers.get("user-agent")
        await self.admin_repo.create_audit_log(
            admin_id=admin.id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip,
            user_agent=ua,
            details=details,
        )
        await self.db.commit()

    # ── Dashboard Stats ──────────────────────────────────────────────────────

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        raw = await self.admin_repo.get_dashboard_stats()
        return AdminDashboardStats(
            users=UserStats(**raw["users"]),
            startups=StartupStats(**raw["startups"]),
            predictions=PredictionStats(**raw["predictions"]),
            reports=ReportStats(**raw["reports"]),
            franchises=FranchiseStats(**raw["franchises"]),
        )

    # ── User Management ──────────────────────────────────────────────────────

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> AdminUserListResponse:
        users, total = await self.admin_repo.get_users_paginated(
            page=page, per_page=per_page,
            search=search, role=role,
            is_active=is_active, is_verified=is_verified,
        )

        items = []
        for u in users:
            sc = await self.admin_repo.get_user_startup_count(u.id)
            ac = await self.admin_repo.get_user_analysis_count(u.id)
            rc = await self.admin_repo.get_user_report_count(u.id)
            items.append(AdminUserOut(
                id=u.id,
                full_name=u.full_name,
                email=u.email,
                role=str(u.role.value if hasattr(u.role, 'value') else u.role),
                is_active=u.is_active,
                is_verified=u.is_verified,
                created_at=u.created_at,
                updated_at=u.updated_at if hasattr(u, 'updated_at') else None,
                startup_count=sc,
                analysis_count=ac,
                report_count=rc,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminUserListResponse(items=items, total=total, page=page, per_page=per_page, pages=pages)

    async def get_user_detail(self, user_id: UUID) -> AdminUserDetail:
        data = await self.admin_repo.get_user_with_counts(user_id)
        if not data:
            raise NotFoundException(f"User {user_id} not found.")
        u = data["user"]
        return AdminUserDetail(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role=str(u.role.value if hasattr(u.role, 'value') else u.role),
            is_active=u.is_active,
            is_verified=u.is_verified,
            phone=u.phone,
            location=u.location,
            created_at=u.created_at,
            updated_at=u.updated_at if hasattr(u, 'updated_at') else None,
            startup_count=data["startup_count"],
            analysis_count=data["analysis_count"],
            report_count=data["report_count"],
            recent_startups=data["recent_startups"],
            recent_reports=data["recent_reports"],
        )

    async def update_user_status(
        self,
        user_id: UUID,
        is_active: bool,
        admin: User,
        request: Optional[Request] = None,
    ) -> AdminUserOut:
        from sqlalchemy import select
        res = await self.db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(User).where(User.id == user_id)
        )
        user = res.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found.")

        # Safety: admin cannot deactivate themselves
        if user.id == admin.id and not is_active:
            raise ForbiddenException("You cannot deactivate your own account.")

        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)

        action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
        await self.log_action(admin, action, "user", str(user_id), request,
                              {"target_email": user.email})

        sc = await self.admin_repo.get_user_startup_count(user.id)
        ac = await self.admin_repo.get_user_analysis_count(user.id)
        rc = await self.admin_repo.get_user_report_count(user.id)
        return AdminUserOut(
            id=user.id, full_name=user.full_name, email=user.email,
            role=str(user.role.value if hasattr(user.role, 'value') else user.role),
            is_active=user.is_active, is_verified=user.is_verified,
            created_at=user.created_at,
            startup_count=sc, analysis_count=ac, report_count=rc,
        )

    async def update_user_role(
        self,
        user_id: UUID,
        role: str,
        admin: User,
        request: Optional[Request] = None,
    ) -> AdminUserOut:
        from sqlalchemy import select
        from app.models.models import UserRole
        res = await self.db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(User).where(User.id == user_id)
        )
        user = res.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found.")

        # Safety: admin cannot demote their own role
        if user.id == admin.id and role.lower() != "admin":
            raise ForbiddenException("You cannot remove your own admin privileges.")

        # Map role string to enum
        role_lower = role.lower()
        if role_lower == "admin":
            user.role = UserRole.admin
        elif role_lower == "user":
            user.role = UserRole.user
        else:
            raise BadRequestException(f"Invalid role: {role}")

        await self.db.commit()
        await self.db.refresh(user)

        await self.log_action(admin, "USER_ROLE_CHANGED", "user", str(user_id), request,
                              {"new_role": role, "target_email": user.email})

        sc = await self.admin_repo.get_user_startup_count(user.id)
        ac = await self.admin_repo.get_user_analysis_count(user.id)
        rc = await self.admin_repo.get_user_report_count(user.id)
        return AdminUserOut(
            id=user.id, full_name=user.full_name, email=user.email,
            role=str(user.role.value if hasattr(user.role, 'value') else user.role),
            is_active=user.is_active, is_verified=user.is_verified,
            created_at=user.created_at,
            startup_count=sc, analysis_count=ac, report_count=rc,
        )

    async def delete_user(
        self,
        user_id: UUID,
        admin: User,
        request: Optional[Request] = None,
    ) -> Dict[str, str]:
        from sqlalchemy import select
        res = await self.db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(User).where(User.id == user_id)
        )
        user = res.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found.")

        if user.id == admin.id:
            raise ForbiddenException("You cannot delete your own account.")

        target_email = user.email
        await self.log_action(admin, "USER_DELETED", "user", str(user_id), request,
                              {"deleted_email": target_email})

        await self.db.delete(user)
        await self.db.commit()
        return {"message": f"User {target_email} deleted successfully."}

    # ── Startups ─────────────────────────────────────────────────────────────

    async def list_startups(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> AdminStartupListResponse:
        items, total = await self.admin_repo.get_startups_paginated(
            page=page, per_page=per_page,
            search=search, category=category, risk_level=risk_level,
        )

        out_items = []
        for row in items:
            s = row["startup"]
            owner = row["owner"]
            pred = row["prediction"]
            out_items.append(AdminStartupOut(
                id=s.id,
                business_name=s.business_name,
                owner_name=owner.full_name if owner else "Unknown",
                owner_email=owner.email if owner else "",
                business_category=s.business_category,
                preferred_location=s.preferred_location,
                investment_amount=s.investment_amount,
                success_probability=pred.success_probability if pred else None,
                risk_level=pred.risk_level if pred else None,
                estimated_roi=pred.estimated_roi if pred else None,
                business_score=pred.business_score if pred else None,
                has_prediction=pred is not None,
                created_at=s.created_at,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminStartupListResponse(items=out_items, total=total, page=page, per_page=per_page, pages=pages)

    async def get_startup_detail(self, startup_id: UUID, admin: User, request: Optional[Request] = None) -> AdminStartupDetail:
        data = await self.admin_repo.get_startup_admin_detail(startup_id)
        if not data:
            raise NotFoundException(f"Startup {startup_id} not found.")

        await self.log_action(admin, "STARTUP_VIEWED", "startup", str(startup_id), request)

        s = data["startup"]
        owner = data["owner"]
        pred = data["prediction"]

        pred_dict = None
        if pred:
            pred_dict = {
                "id": str(pred.id),
                "success_probability": pred.success_probability,
                "business_score": pred.business_score,
                "risk_level": pred.risk_level,
                "estimated_roi": pred.estimated_roi,
                "competition_score": pred.competition_score,
                "confidence_score": pred.confidence_score,
                "created_at": pred.created_at.isoformat(),
            }

        return AdminStartupDetail(
            id=s.id,
            business_name=s.business_name,
            owner_name=owner.full_name if owner else "Unknown",
            owner_email=owner.email if owner else "",
            business_category=s.business_category,
            business_model=s.business_model,
            preferred_location=s.preferred_location,
            target_customers=s.target_customers,
            investment_amount=s.investment_amount,
            expected_monthly_revenue=s.expected_monthly_revenue,
            market_demand=s.market_demand,
            competition_level=s.competition_level,
            experience_years=s.experience_years,
            employee_count=s.employee_count,
            description=s.description,
            created_at=s.created_at,
            prediction=pred_dict,
            franchise_recs_count=data["franchise_recs_count"],
            marketing_count=data["marketing_count"],
            reports_count=data["reports_count"],
        )

    # ── Predictions ──────────────────────────────────────────────────────────

    async def list_predictions(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> AdminPredictionListResponse:
        items, total = await self.admin_repo.get_predictions_paginated(
            page=page, per_page=per_page, search=search,
        )

        out_items = []
        for row in items:
            pred = row["prediction"]
            startup = row["startup"]
            owner = row["owner"]
            out_items.append(AdminPredictionOut(
                id=pred.id,
                startup_id=pred.startup_id,
                startup_name=startup.business_name,
                owner_name=owner.full_name,
                success_probability=pred.success_probability,
                business_score=pred.business_score,
                risk_level=pred.risk_level,
                estimated_roi=pred.estimated_roi,
                competition_score=pred.competition_score,
                confidence_score=pred.confidence_score,
                created_at=pred.created_at,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminPredictionListResponse(items=out_items, total=total, page=page, per_page=per_page, pages=pages)

    # ── Franchises ───────────────────────────────────────────────────────────

    async def list_franchises_admin(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        industry: Optional[str] = None,
    ) -> AdminFranchiseListResponse:
        franchises, total = await self.admin_repo.get_franchises_admin_paginated(
            page=page, per_page=per_page,
            search=search, is_active=is_active, industry=industry,
        )

        items = [_franchise_to_out(f) for f in franchises]
        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminFranchiseListResponse(items=items, total=total, page=page, per_page=per_page, pages=pages)

    async def get_franchise_admin(self, franchise_id: UUID) -> AdminFranchiseOut:
        f = await self.franchise_repo.get_by_id(franchise_id)
        if not f:
            raise NotFoundException(f"Franchise {franchise_id} not found.")
        return _franchise_to_out(f)

    async def create_franchise_admin(
        self,
        payload: AdminFranchiseCreate,
        admin: User,
        request: Optional[Request] = None,
    ) -> AdminFranchiseOut:
        franchise = Franchise(
            franchise_name=payload.franchise_name,
            industry=payload.industry,
            business_model=payload.business_model,
            minimum_investment=payload.minimum_investment,
            maximum_investment=payload.maximum_investment,
            roi=payload.roi,
            risk_level=payload.risk_level,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            experience_required=payload.experience_required,
            market_demand=payload.market_demand,
            target_customer=payload.target_customer,
            description=payload.description,
            advantages=payload.advantages,
            disadvantages=payload.disadvantages,
            website=payload.website,
            contact_email=payload.contact_email,
            logo_url=payload.logo_url,
            is_active=payload.is_active,
        )
        self.db.add(franchise)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(franchise)

        await self.log_action(admin, "FRANCHISE_CREATED", "franchise", str(franchise.id), request,
                              {"name": franchise.franchise_name})
        return _franchise_to_out(franchise)

    async def update_franchise_admin(
        self,
        franchise_id: UUID,
        payload: AdminFranchiseUpdate,
        admin: User,
        request: Optional[Request] = None,
    ) -> AdminFranchiseOut:
        f = await self.franchise_repo.get_by_id(franchise_id)
        if not f:
            raise NotFoundException(f"Franchise {franchise_id} not found.")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(f, field, value)

        await self.db.commit()
        await self.db.refresh(f)

        await self.log_action(admin, "FRANCHISE_UPDATED", "franchise", str(franchise_id), request,
                              {"name": f.franchise_name, "fields": list(update_data.keys())})
        return _franchise_to_out(f)

    async def delete_franchise_admin(
        self,
        franchise_id: UUID,
        admin: User,
        request: Optional[Request] = None,
    ) -> Dict[str, str]:
        f = await self.franchise_repo.get_by_id(franchise_id)
        if not f:
            raise NotFoundException(f"Franchise {franchise_id} not found.")

        name = f.franchise_name
        await self.log_action(admin, "FRANCHISE_DELETED", "franchise", str(franchise_id), request,
                              {"name": name})
        await self.db.delete(f)
        await self.db.commit()
        return {"message": f"Franchise '{name}' deleted successfully."}

    async def toggle_franchise_status(
        self,
        franchise_id: UUID,
        is_active: bool,
        admin: User,
        request: Optional[Request] = None,
    ) -> AdminFranchiseOut:
        f = await self.franchise_repo.get_by_id(franchise_id)
        if not f:
            raise NotFoundException(f"Franchise {franchise_id} not found.")
        f.is_active = is_active
        await self.db.commit()
        await self.db.refresh(f)

        action = "FRANCHISE_ACTIVATED" if is_active else "FRANCHISE_DEACTIVATED"
        await self.log_action(admin, action, "franchise", str(franchise_id), request,
                              {"name": f.franchise_name})
        return _franchise_to_out(f)

    # ── Marketing ────────────────────────────────────────────────────────────

    async def list_marketing_admin(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> AdminMarketingListResponse:
        items, total = await self.admin_repo.get_marketing_paginated(
            page=page, per_page=per_page, search=search,
        )

        out_items = []
        for row in items:
            s = row["strategy"]
            owner = row["owner"]
            startup = row["startup"]
            out_items.append(AdminMarketingOut(
                id=s.id,
                strategy_name=s.strategy_name,
                business_category=s.business_category,
                platform=s.platform,
                total_budget=s.total_budget,
                strategy_type=s.strategy_type,
                marketing_score=s.marketing_score,
                startup_id=s.startup_id,
                startup_name=startup.business_name if startup else None,
                owner_name=owner.full_name if owner else None,
                created_at=s.created_at,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminMarketingListResponse(items=out_items, total=total, page=page, per_page=per_page, pages=pages)

    async def delete_marketing_admin(
        self,
        strategy_id: UUID,
        admin: User,
        request: Optional[Request] = None,
    ) -> Dict[str, str]:
        from sqlalchemy import select
        res = await self.db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(MarketingStrategy).where(MarketingStrategy.id == strategy_id)
        )
        strategy = res.scalar_one_or_none()
        if not strategy:
            raise NotFoundException(f"Marketing strategy {strategy_id} not found.")

        name = strategy.strategy_name
        await self.log_action(admin, "MARKETING_DELETED", "marketing_strategy", str(strategy_id), request,
                              {"name": name})
        await self.db.delete(strategy)
        await self.db.commit()
        return {"message": f"Marketing strategy '{name}' deleted."}

    # ── Reports ──────────────────────────────────────────────────────────────

    async def list_reports_admin(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> AdminReportListResponse:
        items, total = await self.admin_repo.get_reports_paginated(
            page=page, per_page=per_page, search=search,
        )

        out_items = []
        for row in items:
            r = row["report"]
            owner = row["owner"]
            startup = row["startup"]
            out_items.append(AdminReportOut(
                id=r.id,
                title=r.title,
                user_id=r.user_id,
                owner_name=owner.full_name if owner else "Unknown",
                owner_email=owner.email if owner else "",
                startup_id=r.startup_id,
                startup_name=startup.business_name if startup else None,
                generated_at=r.generated_at,
                has_file=bool(r.pdf_path),
                pdf_path=r.pdf_path,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminReportListResponse(items=out_items, total=total, page=page, per_page=per_page, pages=pages)

    async def delete_report_admin(
        self,
        report_id: UUID,
        admin: User,
        request: Optional[Request] = None,
    ) -> Dict[str, str]:
        from sqlalchemy import select
        res = await self.db.execute(
            __import__('sqlalchemy', fromlist=['select']).select(Report).where(Report.id == report_id)
        )
        report = res.scalar_one_or_none()
        if not report:
            raise NotFoundException(f"Report {report_id} not found.")

        title = report.title
        await self.log_action(admin, "REPORT_DELETED", "report", str(report_id), request,
                              {"title": title})
        await self.db.delete(report)
        await self.db.commit()
        return {"message": f"Report '{title}' deleted successfully."}

    # ── ML Monitoring ────────────────────────────────────────────────────────

    async def get_ml_info(self) -> AdminMLResponse:
        manager = get_model_manager()
        health = manager.get_health_status()

        model_algo_map = {
            "success": "Random Forest Classifier",
            "risk": "Random Forest Classifier",
            "roi": "Gradient Boosting Regressor",
            "competition": "Random Forest Classifier",
        }

        models_list = []
        for name in ["success", "risk", "roi", "competition"]:
            loaded = health.get("models", {}).get(name, False)
            models_list.append(ModelInfo(
                name=f"{name.title()} Model",
                algorithm=model_algo_map.get(name),
                version="1.0.0",
                status="loaded" if loaded else "not_loaded",
                loaded=loaded,
            ))

        preprocessors_list = []
        for name in ["success", "risk", "roi", "competition"]:
            loaded = health.get("preprocessors", {}).get(name, False)
            preprocessors_list.append(ModelInfo(
                name=f"{name.title()} Preprocessor",
                algorithm="ColumnTransformer + StandardScaler",
                version="1.0.0",
                status="loaded" if loaded else "not_loaded",
                loaded=loaded,
            ))

        services = [
            ServiceHealthItem(
                name="ML Engine",
                status="healthy" if health.get("models_loaded") else "degraded",
                message="All models loaded" if health.get("models_loaded") else health.get("error", "Models not loaded"),
            ),
            ServiceHealthItem(
                name="Preprocessors",
                status="healthy" if all(health.get("preprocessors", {}).values()) else "degraded",
                message="All preprocessors loaded" if all(health.get("preprocessors", {}).values()) else "Some preprocessors missing",
            ),
            ServiceHealthItem(name="Database", status="healthy", message="Connected"),
            ServiceHealthItem(name="Prediction Service", status="healthy" if health.get("models_loaded") else "degraded"),
            ServiceHealthItem(name="Recommendation Service", status="healthy"),
        ]

        metrics = manager.model_metrics if manager.model_metrics else {}

        return AdminMLResponse(
            models=models_list,
            preprocessors=preprocessors_list,
            services=services,
            metrics=metrics,
            artifacts_dir=str(health.get("artifacts_dir", "")),
            is_fully_loaded=bool(health.get("models_loaded")),
        )

    # ── Audit Logs ───────────────────────────────────────────────────────────

    async def list_audit_logs(
        self,
        page: int = 1,
        per_page: int = 50,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AdminAuditLogListResponse:
        items, total = await self.admin_repo.get_audit_logs_paginated(
            page=page, per_page=per_page,
            action=action, resource=resource,
            start_date=start_date, end_date=end_date,
        )

        out_items = []
        for row in items:
            log = row["log"]
            admin_user = row["admin"]
            out_items.append(AdminAuditLogOut(
                id=log.id,
                timestamp=log.created_at,
                admin_name=admin_user.full_name if admin_user else "System",
                admin_email=admin_user.email if admin_user else None,
                action=log.action,
                resource=log.resource,
                resource_id=row.get("resource_id"),
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                details=log.details,
            ))

        pages = ceil(total / per_page) if per_page > 0 else 1
        return AdminAuditLogListResponse(items=out_items, total=total, page=page, per_page=per_page, pages=pages)

    # ── Analytics ────────────────────────────────────────────────────────────

    async def get_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> AdminAnalyticsResponse:
        data = await self.admin_repo.get_analytics_timeseries(
            start_date=start_date, end_date=end_date, group_by=group_by,
        )

        def to_ts_points(raw: List[Dict]) -> List[TimeSeriesPoint]:
            return [TimeSeriesPoint(date=str(r["date"]), value=float(r["value"])) for r in raw]

        def to_dist_items(raw: List[Dict]) -> List[DistributionItem]:
            return [DistributionItem(label=r["label"], count=r["count"], percentage=r["percentage"]) for r in raw]

        return AdminAnalyticsResponse(
            user_growth=to_ts_points(data.get("user_trend", [])),
            startup_creation=to_ts_points(data.get("startup_trend", [])),
            analysis_volume=to_ts_points(data.get("prediction_trend", [])),
            risk_distribution=to_dist_items(data.get("risk_distribution", [])),
            success_distribution=[],
            category_distribution=to_dist_items(data.get("category_distribution", [])),
            avg_business_score_trend=to_ts_points(data.get("score_trend", [])),
            avg_roi_trend=[],
            report_generation=to_ts_points(data.get("report_trend", [])),
            franchise_rec_volume=[],
            period_start=start_date.isoformat() if start_date else None,
            period_end=end_date.isoformat() if end_date else None,
        )

    # ── Settings ─────────────────────────────────────────────────────────────

    async def get_settings(self) -> AdminSettingsResponse:
        from app.core.config import settings
        import os

        resend_key = os.environ.get("RESEND_API_KEY", "")
        email_configured = bool(resend_key and len(resend_key) > 10)

        manager = get_model_manager()
        ml_health = manager.get_health_status()

        return AdminSettingsResponse(
            platform={
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG,
            },
            email={
                "provider": "Resend",
                "api_key_status": "Configured" if email_configured else "Not Configured",
                "from_name": "STARTWISE AI",
                "from_address": "noreply@startwise.ai",
            },
            ml={
                "model_version": "1.0.0",
                "models_loaded": ml_health.get("models_loaded", False),
                "artifacts_dir": str(ml_health.get("artifacts_dir", "")),
                "model_health": "healthy" if ml_health.get("models_loaded") else "degraded",
                "retraining": "Available through offline ML training pipeline only",
            },
            security={
                "jwt_configured": True,
                "database_configured": True,
                "rate_limiting": f"{settings.RATE_LIMIT_REQUESTS} req/{settings.RATE_LIMIT_PERIOD}s",
            },
        )


# ── Helper ───────────────────────────────────────────────────────────────────

def _franchise_to_out(f: Franchise) -> AdminFranchiseOut:
    return AdminFranchiseOut(
        id=f.id,
        franchise_name=f.franchise_name,
        industry=f.industry,
        business_model=f.business_model,
        minimum_investment=f.minimum_investment,
        maximum_investment=f.maximum_investment,
        roi=f.roi,
        risk_level=f.risk_level,
        city=f.city,
        state=f.state,
        country=f.country,
        experience_required=f.experience_required,
        market_demand=f.market_demand,
        target_customer=f.target_customer,
        description=f.description,
        advantages=f.advantages,
        disadvantages=f.disadvantages,
        website=f.website,
        contact_email=f.contact_email,
        logo_url=f.logo_url,
        is_active=f.is_active,
        created_at=f.created_at,
        updated_at=f.updated_at if hasattr(f, 'updated_at') else None,
    )
