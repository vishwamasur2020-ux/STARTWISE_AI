"""
STARTWISE AI — Admin Repository (Stage 12)
Data access layer for all admin-specific aggregated queries.
Uses SQLAlchemy 2.0 async with efficient joins to avoid N+1.
"""

from datetime import datetime, timezone
from math import ceil
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, desc, asc, and_, or_, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.models import (
    User, UserRole, StartupIdea, PredictionResult,
    Franchise, FranchiseRecommendation, MarketingStrategy,
    Report, AuditLog,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Dashboard Stats ──────────────────────────────────────────────────────

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Single-pass aggregated stats for admin KPI cards."""
        # Users
        user_total = await self.db.execute(select(func.count(User.id)))
        user_active = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )

        # Startups
        startup_total = await self.db.execute(select(func.count(StartupIdea.id)))

        # Predictions aggregates
        pred_count = await self.db.execute(select(func.count(PredictionResult.id)))
        pred_avg_score = await self.db.execute(
            select(func.avg(PredictionResult.business_score))
        )
        pred_avg_success = await self.db.execute(
            select(func.avg(PredictionResult.success_probability))
        )
        pred_avg_roi = await self.db.execute(
            select(func.avg(PredictionResult.estimated_roi))
        )
        pred_high_risk = await self.db.execute(
            select(func.count(PredictionResult.id)).where(
                func.lower(PredictionResult.risk_level) == "high"
            )
        )

        # Reports
        report_total = await self.db.execute(select(func.count(Report.id)))

        # Franchises
        franchise_total = await self.db.execute(select(func.count(Franchise.id)))

        return {
            "users": {
                "total": user_total.scalar_one() or 0,
                "active": user_active.scalar_one() or 0,
            },
            "startups": {
                "total": startup_total.scalar_one() or 0,
            },
            "predictions": {
                "total": pred_count.scalar_one() or 0,
                "average_score": round(float(pred_avg_score.scalar_one() or 0), 1),
                "average_success_probability": round(float(pred_avg_success.scalar_one() or 0), 1),
                "average_roi": round(float(pred_avg_roi.scalar_one() or 0), 1),
                "high_risk_count": pred_high_risk.scalar_one() or 0,
            },
            "reports": {
                "total": report_total.scalar_one() or 0,
                "emails_sent": 0,  # No email tracking column in Report model
            },
            "franchises": {
                "total": franchise_total.scalar_one() or 0,
            },
        }

    # ── User Management ──────────────────────────────────────────────────────

    async def get_users_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    User.full_name.ilike(q),
                    User.email.ilike(q),
                    func.cast(User.id, text("VARCHAR")).ilike(q),
                )
            )

        if role:
            conditions.append(func.lower(func.cast(User.role, text("VARCHAR"))).in_(
                [role.lower(), role.upper()]
            ))

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        if is_verified is not None:
            conditions.append(User.is_verified == is_verified)

        where_clause = and_(*conditions) if conditions else True

        # Count
        count_stmt = select(func.count(User.id)).where(where_clause)
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        # Items
        offset = (page - 1) * per_page
        stmt = (
            select(User)
            .where(where_clause)
            .order_by(desc(User.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        users = list(res.scalars().all())

        return users, total

    async def get_user_with_counts(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Fetch user + startup/analysis/report counts in one go."""
        user_res = await self.db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            return None

        startup_count = await self.db.execute(
            select(func.count(StartupIdea.id)).where(StartupIdea.user_id == user_id)
        )
        analysis_count = await self.db.execute(
            select(func.count(PredictionResult.id))
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(StartupIdea.user_id == user_id)
        )
        report_count = await self.db.execute(
            select(func.count(Report.id)).where(Report.user_id == user_id)
        )

        # Recent startups
        recent_startups_res = await self.db.execute(
            select(StartupIdea)
            .where(StartupIdea.user_id == user_id)
            .order_by(desc(StartupIdea.created_at))
            .limit(5)
        )
        recent_startups = recent_startups_res.scalars().all()

        # Recent reports
        recent_reports_res = await self.db.execute(
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(desc(Report.generated_at))
            .limit(5)
        )
        recent_reports = recent_reports_res.scalars().all()

        return {
            "user": user,
            "startup_count": startup_count.scalar_one() or 0,
            "analysis_count": analysis_count.scalar_one() or 0,
            "report_count": report_count.scalar_one() or 0,
            "recent_startups": [
                {"id": str(s.id), "business_name": s.business_name, "created_at": s.created_at}
                for s in recent_startups
            ],
            "recent_reports": [
                {"id": str(r.id), "title": r.title, "generated_at": r.generated_at}
                for r in recent_reports
            ],
        }

    async def get_user_startup_count(self, user_id: UUID) -> int:
        r = await self.db.execute(
            select(func.count(StartupIdea.id)).where(StartupIdea.user_id == user_id)
        )
        return r.scalar_one() or 0

    async def get_user_analysis_count(self, user_id: UUID) -> int:
        r = await self.db.execute(
            select(func.count(PredictionResult.id))
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(StartupIdea.user_id == user_id)
        )
        return r.scalar_one() or 0

    async def get_user_report_count(self, user_id: UUID) -> int:
        r = await self.db.execute(
            select(func.count(Report.id)).where(Report.user_id == user_id)
        )
        return r.scalar_one() or 0

    # ── Startups Admin ───────────────────────────────────────────────────────

    async def get_startups_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    StartupIdea.business_name.ilike(q),
                    StartupIdea.preferred_location.ilike(q),
                    StartupIdea.business_category.ilike(q),
                )
            )

        if category:
            conditions.append(StartupIdea.business_category.ilike(f"%{category}%"))

        where_clause = and_(*conditions) if conditions else True

        count_stmt = select(func.count(StartupIdea.id)).where(where_clause)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(StartupIdea)
            .where(where_clause)
            .options(
                selectinload(StartupIdea.prediction_result),
                selectinload(StartupIdea.user),
            )
            .order_by(desc(StartupIdea.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        startups = list(res.scalars().all())

        items = []
        for s in startups:
            pred = s.prediction_result
            # Apply risk filter if specified
            if risk_level and pred:
                if pred.risk_level.lower() != risk_level.lower():
                    continue
            items.append({
                "startup": s,
                "owner": s.user,
                "prediction": pred,
            })

        return items, total

    async def get_startup_admin_detail(self, startup_id: UUID) -> Optional[Dict[str, Any]]:
        stmt = (
            select(StartupIdea)
            .where(StartupIdea.id == startup_id)
            .options(
                selectinload(StartupIdea.prediction_result),
                selectinload(StartupIdea.user),
                selectinload(StartupIdea.reports),
            )
        )
        res = await self.db.execute(stmt)
        startup = res.scalar_one_or_none()
        if not startup:
            return None

        # Counts
        fr_count = await self.db.execute(
            select(func.count(FranchiseRecommendation.id))
            .where(FranchiseRecommendation.startup_id == startup_id)
        )
        mkt_count = await self.db.execute(
            select(func.count(MarketingStrategy.id))
            .where(MarketingStrategy.startup_id == startup_id)
        )

        return {
            "startup": startup,
            "owner": startup.user,
            "prediction": startup.prediction_result,
            "franchise_recs_count": fr_count.scalar_one() or 0,
            "marketing_count": mkt_count.scalar_one() or 0,
            "reports_count": len(startup.reports),
        }

    # ── Predictions Admin ────────────────────────────────────────────────────

    async def get_predictions_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(StartupIdea.business_name.ilike(q))

        where_clause = and_(*conditions) if conditions else True

        count_stmt = (
            select(func.count(PredictionResult.id))
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(where_clause)
        )
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(PredictionResult, StartupIdea, User)
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .join(User, StartupIdea.user_id == User.id)
            .where(where_clause)
            .order_by(desc(PredictionResult.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        items = [
            {"prediction": row[0], "startup": row[1], "owner": row[2]}
            for row in rows
        ]
        return items, total

    # ── Franchises Admin ─────────────────────────────────────────────────────

    async def get_franchises_admin_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        industry: Optional[str] = None,
    ) -> Tuple[List[Franchise], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    Franchise.franchise_name.ilike(q),
                    Franchise.industry.ilike(q),
                    Franchise.city.ilike(q),
                )
            )

        if is_active is not None:
            conditions.append(Franchise.is_active == is_active)

        if industry:
            conditions.append(Franchise.industry.ilike(f"%{industry}%"))

        where_clause = and_(*conditions) if conditions else True

        count_stmt = select(func.count(Franchise.id)).where(where_clause)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(Franchise)
            .where(where_clause)
            .order_by(desc(Franchise.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total

    # ── Marketing Admin ──────────────────────────────────────────────────────

    async def get_marketing_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    MarketingStrategy.strategy_name.ilike(q),
                    MarketingStrategy.business_category.ilike(q),
                )
            )

        where_clause = and_(*conditions) if conditions else True

        count_stmt = select(func.count(MarketingStrategy.id)).where(where_clause)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(MarketingStrategy)
            .where(where_clause)
            .options(selectinload(MarketingStrategy.user), selectinload(MarketingStrategy.startup_idea))
            .order_by(desc(MarketingStrategy.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        strategies = list(res.scalars().all())

        items = [
            {
                "strategy": s,
                "owner": s.user,
                "startup": s.startup_idea,
            }
            for s in strategies
        ]
        return items, total

    # ── Reports Admin ────────────────────────────────────────────────────────

    async def get_reports_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conditions = []

        if search:
            q = f"%{search}%"
            conditions.append(
                or_(
                    Report.title.ilike(q),
                    User.email.ilike(q),
                    User.full_name.ilike(q),
                )
            )

        count_stmt = (
            select(func.count(Report.id))
            .join(User, Report.user_id == User.id)
            .where(and_(*conditions) if conditions else True)
        )
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(Report, User, StartupIdea)
            .join(User, Report.user_id == User.id)
            .outerjoin(StartupIdea, Report.startup_id == StartupIdea.id)
            .where(and_(*conditions) if conditions else True)
            .order_by(desc(Report.generated_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        items = [
            {"report": row[0], "owner": row[1], "startup": row[2]}
            for row in rows
        ]
        return items, total

    # ── Audit Logs ───────────────────────────────────────────────────────────

    async def get_audit_logs_paginated(
        self,
        page: int = 1,
        per_page: int = 50,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conditions = []

        if action:
            conditions.append(func.lower(AuditLog.action).contains(action.lower()))

        if resource:
            conditions.append(func.lower(AuditLog.resource).contains(resource.lower()))

        if start_date:
            conditions.append(AuditLog.created_at >= start_date)

        if end_date:
            conditions.append(AuditLog.created_at <= end_date)

        where_clause = and_(*conditions) if conditions else True

        count_stmt = select(func.count(AuditLog.id)).where(where_clause)
        total = (await self.db.execute(count_stmt)).scalar_one() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(AuditLog)
            .where(where_clause)
            .options(selectinload(AuditLog.user))
            .order_by(desc(AuditLog.created_at))
            .offset(offset)
            .limit(per_page)
        )
        res = await self.db.execute(stmt)
        logs = list(res.scalars().all())

        items = []
        for log in logs:
            details = log.details or {}
            items.append({
                "log": log,
                "admin": log.user,
                "resource_id": details.get("resource_id"),
            })

        return items, total

    # ── Analytics ────────────────────────────────────────────────────────────

    async def get_analytics_timeseries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> Dict[str, Any]:
        """Return grouped time-series counts for platform analytics."""
        # Date formatting depends on DB dialect. Use strftime for SQLite, to_char for PG.
        # Detect from session bind
        try:
            dialect_name = self.db.bind.dialect.name if hasattr(self.db, "bind") and self.db.bind else "sqlite"
        except Exception:
            dialect_name = "sqlite"

        if group_by == "month":
            if dialect_name == "postgresql":
                date_trunc = func.to_char(StartupIdea.created_at, "YYYY-MM")
            else:
                date_trunc = func.strftime("%Y-%m", StartupIdea.created_at)
        else:
            if dialect_name == "postgresql":
                date_trunc = func.to_char(StartupIdea.created_at, "YYYY-MM-DD")
            else:
                date_trunc = func.strftime("%Y-%m-%d", StartupIdea.created_at)

        time_conditions = []
        if start_date:
            time_conditions.append(StartupIdea.created_at >= start_date)
        if end_date:
            time_conditions.append(StartupIdea.created_at <= end_date)

        # Startup creation trend
        startup_stmt = (
            select(date_trunc.label("date"), func.count(StartupIdea.id).label("count"))
            .where(and_(*time_conditions) if time_conditions else True)
            .group_by("date")
            .order_by("date")
        )
        startup_res = await self.db.execute(startup_stmt)
        startup_trend = [{"date": row[0], "value": row[1]} for row in startup_res.all()]

        # User growth trend
        if group_by == "month":
            if dialect_name == "postgresql":
                user_date = func.to_char(User.created_at, "YYYY-MM")
            else:
                user_date = func.strftime("%Y-%m", User.created_at)
        else:
            if dialect_name == "postgresql":
                user_date = func.to_char(User.created_at, "YYYY-MM-DD")
            else:
                user_date = func.strftime("%Y-%m-%d", User.created_at)

        user_time_conditions = []
        if start_date:
            user_time_conditions.append(User.created_at >= start_date)
        if end_date:
            user_time_conditions.append(User.created_at <= end_date)

        user_stmt = (
            select(user_date.label("date"), func.count(User.id).label("count"))
            .where(and_(*user_time_conditions) if user_time_conditions else True)
            .group_by("date")
            .order_by("date")
        )
        user_res = await self.db.execute(user_stmt)
        user_trend = [{"date": row[0], "value": row[1]} for row in user_res.all()]

        # Prediction volume trend
        if group_by == "month":
            if dialect_name == "postgresql":
                pred_date = func.to_char(PredictionResult.created_at, "YYYY-MM")
            else:
                pred_date = func.strftime("%Y-%m", PredictionResult.created_at)
        else:
            if dialect_name == "postgresql":
                pred_date = func.to_char(PredictionResult.created_at, "YYYY-MM-DD")
            else:
                pred_date = func.strftime("%Y-%m-%d", PredictionResult.created_at)

        pred_time_conditions = []
        if start_date:
            pred_time_conditions.append(PredictionResult.created_at >= start_date)
        if end_date:
            pred_time_conditions.append(PredictionResult.created_at <= end_date)

        pred_stmt = (
            select(pred_date.label("date"), func.count(PredictionResult.id).label("count"))
            .where(and_(*pred_time_conditions) if pred_time_conditions else True)
            .group_by("date")
            .order_by("date")
        )
        pred_res = await self.db.execute(pred_stmt)
        pred_trend = [{"date": row[0], "value": row[1]} for row in pred_res.all()]

        # Risk distribution
        risk_stmt = (
            select(PredictionResult.risk_level, func.count(PredictionResult.id))
            .group_by(PredictionResult.risk_level)
        )
        risk_res = await self.db.execute(risk_stmt)
        risk_rows = risk_res.all()
        risk_total = sum(r[1] for r in risk_rows) or 1
        risk_dist = [
            {"label": r[0], "count": r[1], "percentage": round(r[1] / risk_total * 100, 1)}
            for r in risk_rows
        ]

        # Category distribution
        cat_stmt = (
            select(StartupIdea.business_category, func.count(StartupIdea.id))
            .group_by(StartupIdea.business_category)
            .order_by(desc(func.count(StartupIdea.id)))
            .limit(10)
        )
        cat_res = await self.db.execute(cat_stmt)
        cat_rows = cat_res.all()
        cat_total = sum(r[1] for r in cat_rows) or 1
        cat_dist = [
            {"label": r[0], "count": r[1], "percentage": round(r[1] / cat_total * 100, 1)}
            for r in cat_rows
        ]

        # Report trend
        if group_by == "month":
            if dialect_name == "postgresql":
                rep_date = func.to_char(Report.generated_at, "YYYY-MM")
            else:
                rep_date = func.strftime("%Y-%m", Report.generated_at)
        else:
            if dialect_name == "postgresql":
                rep_date = func.to_char(Report.generated_at, "YYYY-MM-DD")
            else:
                rep_date = func.strftime("%Y-%m-%d", Report.generated_at)

        rep_time_conditions = []
        if start_date:
            rep_time_conditions.append(Report.generated_at >= start_date)
        if end_date:
            rep_time_conditions.append(Report.generated_at <= end_date)

        rep_stmt = (
            select(rep_date.label("date"), func.count(Report.id).label("count"))
            .where(and_(*rep_time_conditions) if rep_time_conditions else True)
            .group_by("date")
            .order_by("date")
        )
        rep_res = await self.db.execute(rep_stmt)
        rep_trend = [{"date": row[0], "value": row[1]} for row in rep_res.all()]

        # Avg Business Score trend
        if group_by == "month":
            if dialect_name == "postgresql":
                score_date = func.to_char(PredictionResult.created_at, "YYYY-MM")
            else:
                score_date = func.strftime("%Y-%m", PredictionResult.created_at)
        else:
            if dialect_name == "postgresql":
                score_date = func.to_char(PredictionResult.created_at, "YYYY-MM-DD")
            else:
                score_date = func.strftime("%Y-%m-%d", PredictionResult.created_at)

        score_stmt = (
            select(score_date.label("date"), func.avg(PredictionResult.business_score).label("avg_score"))
            .where(and_(*pred_time_conditions) if pred_time_conditions else True)
            .group_by("date")
            .order_by("date")
        )
        score_res = await self.db.execute(score_stmt)
        score_trend = [
            {"date": row[0], "value": round(float(row[1] or 0), 1)}
            for row in score_res.all()
        ]

        return {
            "user_trend": user_trend,
            "startup_trend": startup_trend,
            "prediction_trend": pred_trend,
            "risk_distribution": risk_dist,
            "category_distribution": cat_dist,
            "report_trend": rep_trend,
            "score_trend": score_trend,
        }

    # ── Create Audit Log ─────────────────────────────────────────────────────

    async def create_audit_log(
        self,
        admin_id: UUID,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        log_details = details or {}
        if resource_id:
            log_details["resource_id"] = resource_id

        log = AuditLog(
            user_id=admin_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            details=log_details,
        )
        self.db.add(log)
        await self.db.flush()
        return log
