"""
STARTWISE AI -- Dashboard Aggregation Service (Stage 10)
Aggregates Stage 5 (Startups), Stage 7 (Predictions), Stage 8 (Franchise Recs),
and Stage 9 (Marketing Strategy) into unified, fast API responses.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.models.models import (
    User,
    StartupIdea,
    PredictionResult,
    FranchiseRecommendation,
    MarketingStrategy,
    Report,
    AuditLog,
)
from app.schemas.dashboard_schemas import (
    DashboardResponse,
    UserOverview,
    StartupOverview,
    PredictionOverview,
    FinancialMetrics,
    BusinessHealthDimension,
    FranchiseMatchSummary,
    MarketingSummary,
    PredictionHistoryItem,
    CompletenessChecklist,
    CompletenessItem,
    BusinessInsightItem,
    ActivityItem,
    NotificationItem,
    DashboardStatisticsResponse,
    AnalysisComparisonResponse,
    AnalysisComparisonItem,
)

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_dashboard(
        self, user_id: uuid.UUID, startup_id: Optional[uuid.UUID] = None
    ) -> DashboardResponse:
        """Fetch aggregated dashboard payload for current user."""
        # 1. Fetch user profile
        res_user = await self.db.execute(select(User).where(User.id == user_id))
        user = res_user.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        user_overview = UserOverview(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
        )

        # 1b. If a specific startup_id is requested, verify existence and ownership first
        if startup_id:
            res_target = await self.db.execute(select(StartupIdea).where(StartupIdea.id == startup_id))
            target_st = res_target.scalar_one_or_none()
            if not target_st:
                raise ValueError("Startup idea not found")
            if str(target_st.user_id) != str(user_id):
                raise PermissionError("Access forbidden to this startup idea")

        # 2. Fetch all user startups
        res_all_startups = await self.db.execute(
            select(StartupIdea)
            .where(StartupIdea.user_id == user_id)
            .order_by(desc(StartupIdea.created_at))
        )
        all_startups_models = list(res_all_startups.scalars().all())

        all_startups_overview = [
            StartupOverview(
                id=s.id,
                business_name=s.business_name,
                business_category=s.business_category,
                business_model=s.business_model,
                investment_amount=s.investment_amount,
                expected_monthly_revenue=s.expected_monthly_revenue,
                expected_monthly_expenses=getattr(s, 'expected_monthly_expenses', s.expected_monthly_revenue * 0.45) or (s.expected_monthly_revenue * 0.45),
                preferred_location=s.preferred_location,
                target_customers=s.target_customers,
                experience_years=s.experience_years,
                created_at=s.created_at,
            )
            for s in all_startups_models
        ]

        if not all_startups_models:
            # User has no startups -> Honest Empty State
            return DashboardResponse(
                user=user_overview,
                has_startups=False,
                has_prediction=False,
                completeness=CompletenessChecklist(
                    percentage=0,
                    items=[
                        CompletenessItem(label="Business Information", key="business_info", completed=False),
                        CompletenessItem(label="Financial Information", key="financial_info", completed=False),
                        CompletenessItem(label="Market Information", key="market_info", completed=False),
                        CompletenessItem(label="AI Analysis", key="ai_analysis", completed=False),
                        CompletenessItem(label="Franchise Recommendation", key="franchise_rec", completed=False),
                        CompletenessItem(label="Marketing Strategy", key="marketing_strategy", completed=False),
                    ],
                ),
            )

        # Select target startup (specified ID or default to latest)
        target_startup = None
        if startup_id:
            target_startup = next((s for s in all_startups_models if str(s.id) == str(startup_id)), None)
            if not target_startup:
                # Startup does not belong to user
                raise PermissionError("Access forbidden to this startup idea")
        else:
            target_startup = all_startups_models[0]

        exp_expenses = getattr(target_startup, 'expected_monthly_expenses', target_startup.expected_monthly_revenue * 0.45) or (target_startup.expected_monthly_revenue * 0.45)

        startup_overview = StartupOverview(
            id=target_startup.id,
            business_name=target_startup.business_name,
            business_category=target_startup.business_category,
            business_model=target_startup.business_model,
            investment_amount=target_startup.investment_amount,
            expected_monthly_revenue=target_startup.expected_monthly_revenue,
            expected_monthly_expenses=exp_expenses,
            preferred_location=target_startup.preferred_location,
            target_customers=target_startup.target_customers,
            experience_years=target_startup.experience_years,
            created_at=target_startup.created_at,
        )

        # 3. Fetch latest prediction for target startup
        res_pred = await self.db.execute(
            select(PredictionResult)
            .where(PredictionResult.startup_id == target_startup.id)
            .order_by(desc(PredictionResult.created_at))
        )
        latest_prediction = res_pred.scalars().first()

        prediction_overview = None
        financial_metrics = None
        health_dimensions = []
        if latest_prediction:
            comp_level = getattr(latest_prediction, "competition_level", None)
            if not comp_level:
                comp_score_val = getattr(latest_prediction, "competition_score", 50.0) or 50.0
                comp_level = "High" if comp_score_val >= 70 else ("Medium" if comp_score_val >= 40 else "Low")

            score_label = getattr(latest_prediction, "score_label", None)
            if not score_label:
                bs = latest_prediction.business_score
                score_label = "Excellent" if bs >= 85 else ("Good" if bs >= 70 else ("Moderate" if bs >= 55 else ("High Risk" if bs >= 40 else "Very High Risk")))

            prediction_overview = PredictionOverview(
                id=latest_prediction.id,
                success_probability=round(latest_prediction.success_probability * 100, 1),
                risk_level=latest_prediction.risk_level,
                estimated_roi=round(latest_prediction.estimated_roi, 1),
                competition_level=comp_level,
                business_score=round(latest_prediction.business_score, 1),
                score_label=score_label,
                created_at=latest_prediction.created_at,
            )

            # Financial Calculations
            monthly_prof = target_startup.expected_monthly_revenue - exp_expenses
            annual_prof = monthly_prof * 12.0

            payback_years = None
            payback_label = "Payback period unavailable because estimated annual profit is non-positive."
            if annual_prof > 0:
                payback_years = round(target_startup.investment_amount / annual_prof, 1)
                payback_label = f"{payback_years} Years Payback Period"

            financial_metrics = FinancialMetrics(
                investment_amount=target_startup.investment_amount,
                expected_monthly_revenue=target_startup.expected_monthly_revenue,
                expected_monthly_expenses=exp_expenses,
                monthly_profit=monthly_prof,
                annual_profit=annual_prof,
                estimated_roi=round(latest_prediction.estimated_roi, 1),
                payback_period_years=payback_years,
                payback_period_label=payback_label,
            )

            # Health Dimensions (Radar chart)
            health_dimensions = self._calculate_health_dimensions(target_startup, latest_prediction)

        # 4. Fetch Top 3 Franchise Recommendations
        from app.models.models import Franchise
        res_franchises = await self.db.execute(
            select(FranchiseRecommendation)
            .where(FranchiseRecommendation.startup_id == target_startup.id)
            .order_by(desc(FranchiseRecommendation.match_score))
            .limit(3)
        )
        franchise_models = list(res_franchises.scalars().all())
        franchises_summary = []
        for rec in franchise_models:
            f_name = "Recommended Franchise"
            f_cat = target_startup.business_category
            f_inv = target_startup.investment_amount
            f_risk = "Medium"
            f_loc = target_startup.preferred_location

            res_f = await self.db.execute(select(Franchise).where(Franchise.id == rec.franchise_id))
            f_obj = res_f.scalar_one_or_none()
            if f_obj:
                f_name = f_obj.franchise_name
                f_cat = f_obj.industry
                f_inv = f_obj.minimum_investment
                f_risk = f_obj.risk_level
                f_loc = f_obj.city or target_startup.preferred_location

            why = rec.explanation if isinstance(rec.explanation, list) else [str(rec.explanation or "High compatibility with budget & location")]
            franchises_summary.append(
                FranchiseMatchSummary(
                    id=rec.id,
                    franchise_name=f_name,
                    category=f_cat,
                    investment_required=f_inv,
                    match_score=round(rec.match_score, 1),
                    risk_level=f_risk,
                    location=f_loc,
                    why_recommended=why,
                )
            )

        # 5. Fetch Marketing Strategy Summary
        res_mkt = await self.db.execute(
            select(MarketingStrategy)
            .where(MarketingStrategy.startup_id == target_startup.id)
            .order_by(desc(MarketingStrategy.created_at))
        )
        mkt_model = res_mkt.scalars().first()
        marketing_summary = None
        if mkt_model:
            top_ch = []
            if isinstance(mkt_model.recommended_channels, list):
                top_ch = [
                    {
                        "channel_name": c.get("channel_name", ""),
                        "platform": c.get("platform", ""),
                        "score": c.get("marketing_score", 0),
                        "budget": c.get("allocated_budget", 0),
                    }
                    for c in mkt_model.recommended_channels[:3]
                ]

            marketing_summary = MarketingSummary(
                marketing_score=round(mkt_model.marketing_score, 1),
                strategy_type=mkt_model.strategy_type or "BALANCED",
                recommended_total_budget=mkt_model.total_budget or 0.0,
                top_channels=top_ch,
            )

        # 6. Fetch Prediction History for Line Chart
        res_hist = await self.db.execute(
            select(PredictionResult)
            .where(PredictionResult.startup_id == target_startup.id)
            .order_by(PredictionResult.created_at.asc())
        )
        history_models = list(res_hist.scalars().all())
        history_items = []
        for h in history_models:
            c_lvl = getattr(h, "competition_level", None)
            if not c_lvl:
                c_score = getattr(h, "competition_score", 50.0) or 50.0
                c_lvl = "High" if c_score >= 70 else ("Medium" if c_score >= 40 else "Low")
            history_items.append(
                PredictionHistoryItem(
                    id=h.id,
                    analysis_date=h.created_at,
                    success_probability=round(h.success_probability * 100, 1),
                    risk_level=h.risk_level,
                    estimated_roi=round(h.estimated_roi, 1),
                    business_score=round(h.business_score, 1),
                    competition_level=c_lvl,
                )
            )

        # 7. Completeness Checklist
        completeness = self._calculate_completeness(
            target_startup, latest_prediction, franchises_summary, marketing_summary
        )

        # 8. Dynamic AI Business Insights
        insights = self._generate_dynamic_insights(
            target_startup, latest_prediction, financial_metrics, franchises_summary, marketing_summary
        )

        # 9. Recent User Activities (from AuditLog)
        res_logs = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .limit(5)
        )
        log_models = list(res_logs.scalars().all())
        activity_items = [
            ActivityItem(
                id=l.id,
                action=l.action,
                resource=l.resource,
                details=l.details if isinstance(l.details, dict) else {},
                created_at=l.created_at,
            )
            for l in log_models
        ]

        # 10. Notification Feed
        notifications = self._generate_notifications(
            target_startup, latest_prediction, franchises_summary, marketing_summary
        )

        return DashboardResponse(
            user=user_overview,
            startup=startup_overview,
            all_startups=all_startups_overview,
            prediction=prediction_overview,
            financial=financial_metrics,
            health_dimensions=health_dimensions,
            franchises=franchises_summary,
            marketing=marketing_summary,
            history=history_items,
            completeness=completeness,
            insights=insights,
            activities=activity_items,
            notifications=notifications,
            has_startups=True,
            has_prediction=bool(latest_prediction),
        )

    async def get_dashboard_statistics(self, user_id: uuid.UUID) -> DashboardStatisticsResponse:
        """Calculate overall platform statistics for user."""
        # Total Startups
        res_st_count = await self.db.execute(
            select(func.count(StartupIdea.id)).where(StartupIdea.user_id == user_id)
        )
        total_startups = res_st_count.scalar() or 0

        # Completed Analyses
        res_preds = await self.db.execute(
            select(PredictionResult)
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(StartupIdea.user_id == user_id)
        )
        all_preds = list(res_preds.scalars().all())
        completed_analyses = len(all_preds)

        avg_score = 0.0
        avg_succ = 0.0
        avg_roi = 0.0
        high_risk_count = 0
        if all_preds:
            avg_score = round(sum(p.business_score for p in all_preds) / len(all_preds), 1)
            avg_succ = round(sum(p.success_probability * 100 for p in all_preds) / len(all_preds), 1)
            avg_roi = round(sum(p.estimated_roi for p in all_preds) / len(all_preds), 1)
            high_risk_count = sum(1 for p in all_preds if p.risk_level.lower() == "high")

        # Franchise Recommendations Count
        res_rec_count = await self.db.execute(
            select(func.count(FranchiseRecommendation.id)).where(FranchiseRecommendation.user_id == user_id)
        )
        rec_count = res_rec_count.scalar() or 0

        # Generated Reports Count
        res_rep_count = await self.db.execute(
            select(func.count(Report.id)).where(Report.user_id == user_id)
        )
        rep_count = res_rep_count.scalar() or 0

        return DashboardStatisticsResponse(
            total_startups=total_startups,
            completed_analyses=completed_analyses,
            average_business_score=avg_score,
            average_success_probability=avg_succ,
            average_estimated_roi=avg_roi,
            high_risk_startups_count=high_risk_count,
            recommended_franchises_count=rec_count,
            generated_reports_count=rep_count,
        )

    async def compare_analyses(
        self, user_id: uuid.UUID, id_a: uuid.UUID, id_b: uuid.UUID
    ) -> AnalysisComparisonResponse:
        """Compare two prediction analyses side-by-side."""
        res_a = await self.db.execute(
            select(PredictionResult)
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(and_(PredictionResult.id == id_a, StartupIdea.user_id == user_id))
        )
        pred_a = res_a.scalar_one_or_none()

        res_b = await self.db.execute(
            select(PredictionResult)
            .join(StartupIdea, PredictionResult.startup_id == StartupIdea.id)
            .where(and_(PredictionResult.id == id_b, StartupIdea.user_id == user_id))
        )
        pred_b = res_b.scalar_one_or_none()

        if not pred_a or not pred_b:
            raise ValueError("One or both prediction analysis IDs not found or forbidden")

        bs_a = pred_a.business_score
        label_a = getattr(pred_a, "score_label", None) or ("Excellent" if bs_a >= 85 else ("Good" if bs_a >= 70 else ("Moderate" if bs_a >= 55 else ("High Risk" if bs_a >= 40 else "Very High Risk"))))

        bs_b = pred_b.business_score
        label_b = getattr(pred_b, "score_label", None) or ("Excellent" if bs_b >= 85 else ("Good" if bs_b >= 70 else ("Moderate" if bs_b >= 55 else ("High Risk" if bs_b >= 40 else "Very High Risk"))))

        comp_a = getattr(pred_a, "competition_level", None) or ("High" if (getattr(pred_a, "competition_score", 50) or 50) >= 70 else ("Medium" if (getattr(pred_a, "competition_score", 50) or 50) >= 40 else "Low"))
        comp_b = getattr(pred_b, "competition_level", None) or ("High" if (getattr(pred_b, "competition_score", 50) or 50) >= 70 else ("Medium" if (getattr(pred_b, "competition_score", 50) or 50) >= 40 else "Low"))

        overview_a = PredictionOverview(
            id=pred_a.id,
            success_probability=round(pred_a.success_probability * 100, 1),
            risk_level=pred_a.risk_level,
            estimated_roi=round(pred_a.estimated_roi, 1),
            competition_level=comp_a,
            business_score=round(pred_a.business_score, 1),
            score_label=label_a,
            created_at=pred_a.created_at,
        )

        overview_b = PredictionOverview(
            id=pred_b.id,
            success_probability=round(pred_b.success_probability * 100, 1),
            risk_level=pred_b.risk_level,
            estimated_roi=round(pred_b.estimated_roi, 1),
            competition_level=comp_b,
            business_score=round(pred_b.business_score, 1),
            score_label=label_b,
            created_at=pred_b.created_at,
        )

        delta_score = round(overview_b.business_score - overview_a.business_score, 1)
        delta_succ = round(overview_b.success_probability - overview_a.success_probability, 1)
        delta_roi = round(overview_b.estimated_roi - overview_a.estimated_roi, 1)

        comparisons = [
            AnalysisComparisonItem(
                metric="Business Score",
                value_a=overview_a.business_score,
                value_b=overview_b.business_score,
                delta=delta_score,
                unit="/100",
            ),
            AnalysisComparisonItem(
                metric="Success Probability",
                value_a=overview_a.success_probability,
                value_b=overview_b.success_probability,
                delta=delta_succ,
                unit="%",
            ),
            AnalysisComparisonItem(
                metric="Estimated ROI",
                value_a=overview_a.estimated_roi,
                value_b=overview_b.estimated_roi,
                delta=delta_roi,
                unit="%",
            ),
            AnalysisComparisonItem(
                metric="Risk Level",
                value_a=overview_a.risk_level,
                value_b=overview_b.risk_level,
                delta=None,
                unit="",
            ),
            AnalysisComparisonItem(
                metric="Competition Level",
                value_a=overview_a.competition_level,
                value_b=overview_b.competition_level,
                delta=None,
                unit="",
            ),
        ]

        return AnalysisComparisonResponse(
            analysis_a=overview_a,
            analysis_b=overview_b,
            comparisons=comparisons,
        )

    # ── Helper Calculations ──────────────────────────────────────────────────

    def _calculate_health_dimensions(
        self, startup: StartupIdea, pred: PredictionResult
    ) -> List[BusinessHealthDimension]:
        """Calculate multi-axis radar chart health scores (0-100)."""
        # Financial Health
        rev = startup.expected_monthly_revenue
        exp = getattr(startup, 'expected_monthly_expenses', rev * 0.45) or (rev * 0.45)
        margin = ((rev - exp) / rev * 100) if rev > 0 else 0
        fin_score = min(100.0, max(0.0, (pred.estimated_roi * 0.5) + (margin * 0.5)))

        # Market Demand
        demand_score = min(100.0, max(0.0, (startup.market_demand * 10.0) if hasattr(startup, 'market_demand') and startup.market_demand else (pred.success_probability * 100.0)))

        # Competition Fit (Low competition = high score)
        c_lvl = getattr(pred, "competition_level", None)
        if not c_lvl:
            c_val = getattr(pred, "competition_score", 50.0) or 50.0
            c_lvl = "high" if c_val >= 70 else ("medium" if c_val >= 40 else "low")

        comp_map = {"low": 90.0, "medium": 65.0, "high": 40.0}
        comp_score = comp_map.get(str(c_lvl).lower(), 60.0)

        # Experience Health
        exp_years = getattr(startup, 'experience_years', 0) or 0
        exp_score = min(100.0, max(30.0, exp_years * 15.0))

        # Growth Potential
        growth_score = min(100.0, max(0.0, (pred.success_probability * 60.0) + (pred.estimated_roi * 0.4)))

        # Risk Control Score (Low Risk = 90, High Risk = 30)
        risk_map = {"low": 90.0, "medium": 65.0, "high": 30.0}
        risk_score = risk_map.get(pred.risk_level.lower(), 60.0)

        return [
            BusinessHealthDimension(dimension="Financial Health", score=round(fin_score, 1), label="Financials"),
            BusinessHealthDimension(dimension="Market Demand", score=round(demand_score, 1), label="Demand"),
            BusinessHealthDimension(dimension="Competition Control", score=round(comp_score, 1), label="Competition"),
            BusinessHealthDimension(dimension="Founder Experience", score=round(exp_score, 1), label="Experience"),
            BusinessHealthDimension(dimension="Growth Potential", score=round(growth_score, 1), label="Growth"),
            BusinessHealthDimension(dimension="Risk Safety", score=round(risk_score, 1), label="Risk"),
        ]

    def _calculate_completeness(
        self,
        startup: StartupIdea,
        pred: Optional[PredictionResult],
        franchises: List[FranchiseMatchSummary],
        marketing: Optional[MarketingSummary],
    ) -> CompletenessChecklist:

        has_biz_info = bool(startup.business_name and startup.business_category)
        has_fin_info = bool(startup.investment_amount > 0 and startup.expected_monthly_revenue > 0)
        has_mkt_info = bool(startup.preferred_location and startup.target_customers)
        has_ai_analysis = bool(pred)
        has_franchise = len(franchises) > 0
        has_marketing = bool(marketing)

        items = [
            CompletenessItem(label="Business Information", key="business_info", completed=has_biz_info),
            CompletenessItem(label="Financial Information", key="financial_info", completed=has_fin_info),
            CompletenessItem(label="Market Information", key="market_info", completed=has_mkt_info),
            CompletenessItem(label="AI Analysis", key="ai_analysis", completed=has_ai_analysis),
            CompletenessItem(label="Franchise Recommendation", key="franchise_rec", completed=has_franchise),
            CompletenessItem(label="Marketing Strategy", key="marketing_strategy", completed=has_marketing),
        ]

        completed_count = sum(1 for i in items if i.completed)
        percentage = int(round((completed_count / len(items)) * 100))

        return CompletenessChecklist(percentage=percentage, items=items)

    def _generate_dynamic_insights(
        self,
        startup: StartupIdea,
        pred: Optional[PredictionResult],
        fin: Optional[FinancialMetrics],
        franchises: List[FranchiseMatchSummary],
        marketing: Optional[MarketingSummary],
    ) -> List[BusinessInsightItem]:
        insights = []

        if fin:
            if fin.monthly_profit > 0:
                insights.append(
                    BusinessInsightItem(
                        title="Positive Revenue Margin",
                        type="positive",
                        description=f"Your expected monthly revenue (₹{startup.expected_monthly_revenue:,.0f}) exceeds estimated expenses by ₹{fin.monthly_profit:,.0f} per month.",
                    )
                )
            else:
                insights.append(
                    BusinessInsightItem(
                        title="High Monthly Expenses Alert",
                        type="warning",
                        description="Estimated monthly expenses exceed expected monthly revenue. Review operating cost efficiency before launching.",
                    )
                )

        if pred:
            c_lvl = str(getattr(pred, "competition_level", "medium")).lower()
            if c_lvl == "high":
                insights.append(
                    BusinessInsightItem(
                        title="High Market Competition",
                        type="warning",
                        description="Competition is high in your category. Prioritize unique branding and customer loyalty channels.",
                    )
                )
            else:
                insights.append(
                    BusinessInsightItem(
                        title="Favorable Competitive Landscape",
                        type="positive",
                        description="Market competition is manageable in your target area, creating strong entry opportunities.",
                    )
                )

        if franchises:
            insights.append(
                BusinessInsightItem(
                    title="Proven Franchise Options Available",
                    type="info",
                    description=f"Identified {len(franchises)} verified franchise matches aligned with your budget (₹{startup.investment_amount:,.0f} INR).",
                )
            )

        if marketing:
            insights.append(
                BusinessInsightItem(
                    title="Tailored Marketing Plan Ready",
                    type="action",
                    description=f"Your marketing strategy prioritizes low-acquisition cost channels with a recommended budget of ₹{marketing.recommended_total_budget:,.0f} INR.",
                )
            )

        return insights

    def _generate_notifications(
        self,
        startup: StartupIdea,
        pred: Optional[PredictionResult],
        franchises: List[FranchiseMatchSummary],
        marketing: Optional[MarketingSummary],
    ) -> List[NotificationItem]:
        nots = []
        now = datetime.now(timezone.utc)

        if pred:
            nots.append(
                NotificationItem(
                    id="not-pred-1",
                    title="AI Analysis Complete",
                    message=f"Feasibility prediction for '{startup.business_name}' scored {pred.business_score:.1f}/100.",
                    type="success",
                    timestamp=pred.created_at,
                )
            )

        if franchises:
            nots.append(
                NotificationItem(
                    id="not-fran-1",
                    title="Franchise Matches Available",
                    message=f"Top match: {franchises[0].franchise_name} ({franchises[0].match_score}% fit score).",
                    type="info",
                    timestamp=now,
                )
            )

        if marketing:
            nots.append(
                NotificationItem(
                    id="not-mkt-1",
                    title="Marketing Strategy Generated",
                    message=f"Personalized promotion engine ready with {len(marketing.top_channels)} recommended channels.",
                    type="info",
                    timestamp=now,
                )
            )

        return nots
