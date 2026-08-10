"""
STARTWISE AI — Marketing Service (Stage 9)

High-level business service managing AI Marketing & Promotion Strategy generation,
Stage 7 prediction integration, database persistence, and ownership authorization rules.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, StartupIdea, MarketingStrategy
from app.repositories.marketing_repository import MarketingRepository
from app.repositories.startup_repository import StartupRepository
from app.repositories.prediction_repository import PredictionRepository
from app.marketing.marketing_engine import MarketingRecommendationEngine, MarketingProfile
from app.schemas.marketing_schemas import (
    MarketingStrategyRequest,
    MarketingStrategyResponse,
    MarketingChannelItem,
    CampaignIdeaItem,
    ThirtyDayWeekPhase,
)
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException


class MarketingService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mkt_repo = MarketingRepository(db)
        self.startup_repo = StartupRepository(db)
        self.pred_repo = PredictionRepository(db)
        self.engine = MarketingRecommendationEngine()

    async def analyze_and_create_strategy(
        self,
        req: MarketingStrategyRequest,
        current_user: User,
    ) -> MarketingStrategyResponse:
        """Generate personalized AI marketing strategy for a startup idea."""

        # 1. Fetch startup idea & authorization check
        startup = await self.startup_repo.get_by_id(req.startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only generate marketing strategies for your own startups.")

        # 2. Fetch Stage 7 prediction outputs (Mandatory prerequisite)
        pred = await self.pred_repo.get_latest_by_startup_id(req.startup_id)
        if not pred:
            raise BadRequestException("Complete your AI startup analysis before generating a personalized marketing strategy.")

        # 3. Build Marketing Profile
        comp_level = getattr(startup, "competition_level", None) or ("High" if getattr(pred, "competition_score", 50.0) >= 60.0 else "Medium")

        profile = MarketingProfile(
            category=startup.business_category,
            business_model=startup.business_model or "B2C",
            location=startup.preferred_location or "India",
            target_customer=startup.target_customer or "General Public",
            budget=startup.investment_amount,
            monthly_revenue=startup.expected_monthly_revenue,
            monthly_expenses=getattr(startup, "expected_monthly_expenses", 0.0) or 0.0,
            experience_years=startup.experience_years,
            market_demand=comp_level,
            competition=comp_level,
            predicted_success_probability=pred.success_probability,
            predicted_risk=pred.risk_level,
            predicted_roi=pred.estimated_roi,
            business_score=pred.business_score,
        )

        # 4. Run Marketing Engine
        strategy_dict = self.engine.analyze_and_recommend(profile, top_k=5)

        # 5. Persist to Database
        db_strategy = MarketingStrategy(
            user_id=current_user.id,
            startup_id=startup.id,
            business_category=startup.business_category,
            strategy_name=strategy_dict["strategy_name"],
            platform="Omnichannel",
            total_budget=strategy_dict["total_recommended_budget"],
            strategy_type=strategy_dict["strategy_type"],
            marketing_score=strategy_dict["marketing_score"],
            recommended_channels=strategy_dict["recommended_channels"],
            budget_allocation=strategy_dict["budget_allocation"],
            campaign_ideas=strategy_dict["campaign_ideas"],
            content_strategy=strategy_dict["content_strategy"],
            kpis=strategy_dict["kpis"],
            thirty_day_plan=strategy_dict["thirty_day_plan"],
            description=f"AI Marketing Strategy for {startup.business_name}",
        )

        self.db.add(db_strategy)
        await self.db.commit()
        await self.db.refresh(db_strategy)

        return self._build_response(db_strategy, strategy_dict, startup.id, current_user.id)

    async def get_latest_strategy(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> MarketingStrategyResponse:
        """Retrieve latest marketing strategy for user's startup idea."""
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only view marketing strategies for your own startups.")

        db_strat = await self.mkt_repo.get_latest_by_startup_id(startup_id)
        if not db_strat:
            # Auto-generate if Stage 7 prediction exists
            req = MarketingStrategyRequest(startup_id=startup_id)
            return await self.analyze_and_create_strategy(req, current_user)

        strategy_dict = {
            "strategy_name": db_strat.strategy_name,
            "marketing_score": db_strat.marketing_score,
            "strategy_label": "Strong Strategy",
            "total_recommended_budget": db_strat.total_budget,
            "strategy_type": db_strat.strategy_type,
            "recommended_channels": db_strat.recommended_channels or [],
            "budget_allocation": db_strat.budget_allocation or {},
            "campaign_ideas": db_strat.campaign_ideas or [],
            "content_strategy": db_strat.content_strategy or {},
            "thirty_day_plan": db_strat.thirty_day_plan or [],
            "kpis": db_strat.kpis or [],
            "profile": {
                "category": db_strat.business_category,
                "budget": startup.investment_amount,
                "location": startup.preferred_location,
            },
        }

        return self._build_response(db_strat, strategy_dict, startup.id, current_user.id)

    async def regenerate_strategy(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> MarketingStrategyResponse:
        """Regenerate a new marketing strategy entry."""
        req = MarketingStrategyRequest(startup_id=startup_id)
        return await self.analyze_and_create_strategy(req, current_user)

    def _build_response(
        self,
        db_strat: MarketingStrategy,
        d: Dict[str, Any],
        startup_id: UUID,
        user_id: UUID,
    ) -> MarketingStrategyResponse:
        channels = [MarketingChannelItem.model_validate(c) for c in d.get("recommended_channels", [])]
        campaigns = [CampaignIdeaItem.model_validate(c) for c in d.get("campaign_ideas", [])]
        plan = [ThirtyDayWeekPhase.model_validate(p) for p in d.get("thirty_day_plan", [])]

        return MarketingStrategyResponse(
            id=db_strat.id,
            startup_id=startup_id,
            user_id=user_id,
            strategy_name=d.get("strategy_name", "AI Marketing Strategy"),
            strategy_type=d.get("strategy_type", "BALANCED"),
            marketing_score=d.get("marketing_score", 85.0),
            strategy_label=d.get("strategy_label", "Strong Strategy"),
            total_recommended_budget=d.get("total_recommended_budget", 50000.0),
            profile=d.get("profile", {}),
            recommended_channels=channels,
            budget_allocation=d.get("budget_allocation", {}),
            campaign_ideas=campaigns,
            content_strategy=d.get("content_strategy", {}),
            thirty_day_plan=plan,
            kpis=d.get("kpis", []),
            created_at=db_strat.created_at,
        )
