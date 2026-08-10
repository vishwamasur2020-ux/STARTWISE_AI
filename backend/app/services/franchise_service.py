"""
STARTWISE AI — Franchise Service (Stage 8)

High-level business service managing franchise catalog operations,
personalized hybrid AI recommendation execution, Stage 7 prediction integration,
database persistence, and security/ownership authorization rules.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Franchise, StartupIdea, FranchiseRecommendation
from app.repositories.franchise_repository import FranchiseRepository
from app.repositories.franchise_recommendation_repository import FranchiseRecommendationRepository
from app.repositories.startup_repository import StartupRepository
from app.repositories.prediction_repository import PredictionRepository
from app.recommendation.franchise_recommender import FranchiseRecommender, RecommendedFranchiseResult
from app.schemas.franchise_schemas import (
    FranchiseOut,
    FranchiseRecommendationRequest,
    FranchiseRecommendationResponse,
    FranchiseRecommendationItem,
    FranchiseComparisonResponse,
)
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException


class FranchiseService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.franchise_repo = FranchiseRepository(db)
        self.rec_repo = FranchiseRecommendationRepository(db)
        self.startup_repo = StartupRepository(db)
        self.pred_repo = PredictionRepository(db)

    # ── Catalog Browsing ──────────────────────────────────────────────────────
    async def list_franchises(
        self,
        category: Optional[str] = None,
        min_investment: Optional[float] = None,
        max_investment: Optional[float] = None,
        risk_level: Optional[str] = None,
        city: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[FranchiseOut]:
        franchises = await self.franchise_repo.filter_franchises(
            category=category,
            min_investment=min_investment,
            max_investment=max_investment,
            risk_level=risk_level,
            city=city,
            query=query,
        )
        return [FranchiseOut.model_validate(f) for f in franchises]

    async def get_franchise_by_id(self, franchise_id: UUID) -> FranchiseOut:
        f = await self.franchise_repo.get_by_id(franchise_id)
        if not f or not f.is_active:
            raise NotFoundException("Franchise record not found.")
        return FranchiseOut.model_validate(f)

    async def get_categories(self) -> List[str]:
        return await self.franchise_repo.get_unique_categories()

    async def get_locations(self) -> List[str]:
        return await self.franchise_repo.get_unique_locations()

    # ── Side-by-Side Comparison ───────────────────────────────────────────────
    async def compare_franchises(self, franchise_ids: List[UUID]) -> FranchiseComparisonResponse:
        franchises = []
        for fid in franchise_ids:
            f = await self.franchise_repo.get_by_id(fid)
            if f and f.is_active:
                franchises.append(f)

        if len(franchises) < 2:
            raise BadRequestException("At least 2 valid franchises are required for side-by-side comparison.")

        # Build matrix
        matrix = {
            "investment_range": {str(f.id): f"INR {f.minimum_investment:,.0f} - {f.maximum_investment:,.0f}" for f in franchises},
            "expected_roi": {str(f.id): f"{f.roi:.1f}%" for f in franchises},
            "risk_level": {str(f.id): f.risk_level for f in franchises},
            "industry": {str(f.id): f.industry for f in franchises},
            "city": {str(f.id): f.city or "Nationwide" for f in franchises},
            "experience_required": {str(f.id): f"{f.experience_required} Years" for f in franchises},
            "market_demand": {str(f.id): f"{f.market_demand}/10" for f in franchises},
            "advantages": {str(f.id): f.advantages or [] for f in franchises},
            "disadvantages": {str(f.id): f.disadvantages or [] for f in franchises},
        }

        return FranchiseComparisonResponse(
            franchises=[FranchiseOut.model_validate(f) for f in franchises],
            comparison_matrix=matrix,
        )

    # ── AI Recommendation Engine Integration ────────────────────────────────
    async def generate_recommendations(
        self,
        req: FranchiseRecommendationRequest,
        current_user: User,
    ) -> FranchiseRecommendationResponse:
        stage7_risk: Optional[str] = None
        stage7_roi: Optional[float] = None
        startup: Optional[StartupIdea] = None

        # 1. Authorization check if startup_id provided
        if req.startup_id:
            startup = await self.startup_repo.get_by_id(req.startup_id)
            if not startup:
                raise NotFoundException("Startup idea not found.")
            if startup.user_id != current_user.id and current_user.role != "admin":
                raise ForbiddenException("Access denied. You can only generate recommendations for your own startup ideas.")

            # Load Stage 7 prediction output signals if available
            pred = await self.pred_repo.get_latest_by_startup_id(req.startup_id)
            if pred:
                stage7_risk = pred.risk_level
                stage7_roi = pred.estimated_roi

        # 2. Fetch all active franchises & initialize Recommender
        all_franchises = await self.franchise_repo.get_all_active()
        recommender = FranchiseRecommender(all_franchises)

        # 3. Run Hybrid Recommendation Engine
        rec_results: List[RecommendedFranchiseResult] = recommender.recommend(
            user_budget=req.budget,
            category=req.business_category,
            location=req.location,
            experience_years=req.experience_years,
            expected_roi=req.expected_roi,
            risk_preference=req.risk_preference,
            target_customer=req.target_customer,
            stage7_risk=stage7_risk,
            stage7_roi=stage7_roi,
            top_k=5,
        )

        # 4. Save recommendations to database if startup_id exists
        items: List[FranchiseRecommendationItem] = []

        for res in rec_results:
            item = FranchiseRecommendationItem(
                franchise=FranchiseOut.model_validate(res.franchise),
                match_score=res.match_score,
                score_label=res.score_label,
                ranking_position=res.ranking_position,
                recommendation_type=res.recommendation_type,
                explanation=res.explanation,
                sub_scores=res.sub_scores,
            )
            items.append(item)

            if req.startup_id:
                db_rec = FranchiseRecommendation(
                    user_id=current_user.id,
                    startup_id=req.startup_id,
                    franchise_id=res.franchise.id,
                    match_score=res.match_score,
                    ranking_position=res.ranking_position,
                    recommendation_type=res.recommendation_type,
                    explanation={
                        "score_label": res.score_label,
                        "reasons": res.explanation,
                        "sub_scores": res.sub_scores,
                    },
                )
                self.db.add(db_rec)

        if req.startup_id:
            await self.db.commit()

        return FranchiseRecommendationResponse(
            startup_id=req.startup_id,
            user_budget=req.budget,
            category=req.business_category,
            location=req.location,
            risk_preference=req.risk_preference,
            total_recommendations=len(items),
            recommendations=items,
        )

    async def get_latest_recommendations(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> FranchiseRecommendationResponse:
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only view recommendations for your own startups.")

        db_recs = await self.rec_repo.get_latest_by_startup_id(startup_id)
        if not db_recs:
            # Auto-generate if no history exists
            req = FranchiseRecommendationRequest(
                startup_id=startup.id,
                budget=startup.investment_amount,
                business_category=startup.business_category,
                location=startup.preferred_location,
                experience_years=startup.experience_years,
            )
            return await self.generate_recommendations(req, current_user)

        items = []
        for r in db_recs:
            exp_data = r.explanation or {}
            items.append(
                FranchiseRecommendationItem(
                    franchise=FranchiseOut.model_validate(r.franchise),
                    match_score=r.match_score,
                    score_label=exp_data.get("score_label", "Strong Match"),
                    ranking_position=r.ranking_position,
                    recommendation_type=r.recommendation_type,
                    explanation=exp_data.get("reasons", []),
                    sub_scores=exp_data.get("sub_scores", {}),
                )
            )

        return FranchiseRecommendationResponse(
            startup_id=startup.id,
            user_budget=startup.investment_amount,
            category=startup.business_category,
            location=startup.preferred_location,
            risk_preference="Low",
            total_recommendations=len(items),
            recommendations=items,
        )

    async def refresh_recommendations(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> FranchiseRecommendationResponse:
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only refresh recommendations for your own startups.")

        req = FranchiseRecommendationRequest(
            startup_id=startup.id,
            budget=startup.investment_amount,
            business_category=startup.business_category,
            location=startup.preferred_location,
            experience_years=startup.experience_years,
        )

        return await self.generate_recommendations(req, current_user)
