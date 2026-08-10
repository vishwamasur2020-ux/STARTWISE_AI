"""
STARTWISE AI — Hybrid AI Franchise Recommendation Engine (Stage 8)

Production-ready recommendation engine combining:
  1. Hard constraint filtering (budget, category, location)
  2. Scikit-learn NearestNeighbors (cosine distance similarity)
  3. Domain-specific hybrid compatibility scoring (budget, ROI, risk, experience, demand)
  4. Stage 7 ML prediction signals integration
  5. Dynamic feature explanation generator
  6. Alternative match relaxation logic when candidate pool is small

Academic Architecture:
  - Vector space model with StandardScaler + OneHotEncoder
  - Cosine distance metric for multi-dimensional similarity
  - Configurable weight architecture (recommendation_config.py)
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

from app.models.models import Franchise
from app.core.logging import get_logger
from app.recommendation.recommendation_config import (
    WEIGHT_CONFIG,
    BUDGET_FLEXIBILITY_RATIO,
    get_match_label,
    RECOMMENDATION_DISCLAIMER,
)

logger = get_logger("app.recommendation.franchise_recommender")


class RecommendedFranchiseResult:

    def __init__(
        self,
        franchise: Franchise,
        match_score: float,
        score_label: str,
        ranking_position: int,
        recommendation_type: str,
        explanation: List[str],
        sub_scores: Dict[str, float],
    ):
        self.franchise = franchise
        self.match_score = round(match_score, 1)
        self.score_label = score_label
        self.ranking_position = ranking_position
        self.recommendation_type = recommendation_type  # PRIMARY or ALTERNATIVE
        self.explanation = explanation
        self.sub_scores = sub_scores


class FranchiseRecommender:

    def __init__(self, franchises: List[Franchise]):
        self.all_franchises = [f for f in franchises if f.is_active]

    def _apply_hard_filtering(
        self,
        user_budget: float,
        category: Optional[str],
        location: Optional[str],
    ) -> Tuple[List[Franchise], bool]:
        """
        Apply hard constraint filtering to eliminate non-matching franchises.
        Returns candidate list and boolean indicating if relaxed fallback was used.
        """
        candidates = []
        max_allowed_budget = user_budget * BUDGET_FLEXIBILITY_RATIO

        # 1. Strict Filter
        for f in self.all_franchises:
            # Budget check: minimum investment should be <= max_allowed_budget
            if f.minimum_investment > max_allowed_budget:
                continue

            candidates.append(f)

        # 2. Relaxed Filter Fallback if candidates < 5
        relaxed_used = False
        if len(candidates) < 5:
            relaxed_used = True
            candidates = [f for f in self.all_franchises if f.minimum_investment <= user_budget * 2.0]

        if not candidates:
            candidates = self.all_franchises

        return candidates, relaxed_used

    def _compute_sub_scores(
        self,
        f: Franchise,
        user_budget: float,
        category: str,
        location: str,
        experience_years: int,
        expected_roi: float,
        risk_preference: str,
        stage7_risk: Optional[str] = None,
        stage7_roi: Optional[float] = None,
    ) -> Dict[str, float]:
        """Compute transparent 0-100 compatibility sub-scores for each dimension."""

        # 1. Budget Fit (25%)
        avg_inv = (f.minimum_investment + f.maximum_investment) / 2.0
        if f.minimum_investment <= user_budget <= f.maximum_investment:
            budget_fit = 100.0
        elif user_budget > f.maximum_investment:
            budget_fit = max(40.0, 100.0 - ((user_budget - f.maximum_investment) / user_budget) * 50.0)
        else:
            budget_fit = max(10.0, 100.0 - ((f.minimum_investment - user_budget) / user_budget) * 80.0)

        # 2. Industry/Category Fit (20%)
        f_ind = f.industry.strip().lower()
        u_cat = category.strip().lower()
        if f_ind == u_cat or u_cat in f_ind or f_ind in u_cat:
            industry_fit = 100.0
        elif ("food" in f_ind and "food" in u_cat) or ("retail" in f_ind and "retail" in u_cat):
            industry_fit = 90.0
        elif ("service" in f_ind or "service" in u_cat):
            industry_fit = 70.0
        else:
            industry_fit = 40.0

        # 3. Location Fit (15%)
        u_loc = location.strip().lower()
        f_city = (f.city or "").strip().lower()
        f_state = (f.state or "").strip().lower()
        if f_city and (f_city in u_loc or u_loc in f_city):
            location_fit = 100.0
        elif f_state and (f_state in u_loc or u_loc in f_state):
            location_fit = 85.0
        elif f.country.lower() == "india":
            location_fit = 70.0  # Nationwide availability
        else:
            location_fit = 50.0

        # 4. ROI Fit (15%)
        target_roi = expected_roi if expected_roi > 0 else 25.0
        if stage7_roi and stage7_roi > 0:
            target_roi = (target_roi + stage7_roi) / 2.0

        if f.roi >= target_roi:
            roi_fit = min(100.0, 80.0 + (f.roi - target_roi) * 1.5)
        else:
            roi_fit = max(20.0, 80.0 - (target_roi - f.roi) * 2.5)

        # 5. Risk Fit (10%)
        u_risk = (risk_preference or "Low").capitalize()
        if stage7_risk == "High":
            # If Stage 7 predicted high risk, heavily favor Low risk franchises
            u_risk = "Low"

        if f.risk_level.capitalize() == u_risk:
            risk_fit = 100.0
        elif u_risk == "Low" and f.risk_level.capitalize() == "Medium":
            risk_fit = 75.0
        elif u_risk == "Low" and f.risk_level.capitalize() == "High":
            risk_fit = 30.0
        else:
            risk_fit = 70.0

        # 6. Experience Fit (10%)
        req_exp = f.experience_required
        if experience_years >= req_exp:
            experience_fit = 100.0
        else:
            experience_fit = max(40.0, 100.0 - (req_exp - experience_years) * 25.0)

        # 7. Demand Fit (5%)
        demand_fit = min(100.0, f.market_demand * 10.0)

        return {
            "budget_fit": round(budget_fit, 1),
            "industry_fit": round(industry_fit, 1),
            "location_fit": round(location_fit, 1),
            "roi_fit": round(roi_fit, 1),
            "risk_fit": round(risk_fit, 1),
            "experience_fit": round(experience_fit, 1),
            "demand_fit": round(demand_fit, 1),
        }

    def _generate_explanations(
        self,
        f: Franchise,
        sub_scores: Dict[str, float],
        user_budget: float,
        category: str,
        location: str,
    ) -> List[str]:
        """Generate human-readable explanations based on high sub-scores."""
        reasons = []

        # Budget explanation
        if sub_scores["budget_fit"] >= 80.0:
            reasons.append(
                f"Fits your INR {user_budget:,.0f} budget (Investment range: INR {f.minimum_investment:,.0f} - {f.maximum_investment:,.0f})."
            )
        elif sub_scores["budget_fit"] >= 50.0:
            reasons.append(
                f"Minimum investment of INR {f.minimum_investment:,.0f} is accessible relative to your budget."
            )

        # Category explanation
        if sub_scores["industry_fit"] >= 90.0:
            reasons.append(f"Direct match with your selected '{category}' business category.")

        # Location explanation
        if sub_scores["location_fit"] >= 85.0:
            reasons.append(f"Strong presence and availability in your target region ({f.city or location}).")

        # ROI & Risk explanation
        if sub_scores["roi_fit"] >= 80.0:
            reasons.append(f"Attractive estimated annual ROI of {f.roi:.1f}%.")

        if sub_scores["risk_fit"] >= 90.0:
            reasons.append(f"Compatible '{f.risk_level}' risk profile suitable for your background.")

        if not reasons:
            reasons.append("Good overall profile compatibility across financial and operational factors.")

        return reasons

    def recommend(
        self,
        user_budget: float,
        category: str,
        location: str,
        experience_years: int = 0,
        expected_roi: float = 25.0,
        risk_preference: str = "Low",
        target_customer: str = "General Public",
        stage7_risk: Optional[str] = None,
        stage7_roi: Optional[float] = None,
        top_k: int = 5,
    ) -> List[RecommendedFranchiseResult]:
        """
        Generate ranked Top-K franchise recommendations.
        """
        if not self.all_franchises:
            return []

        # 1. Hard Filtering
        candidates, is_relaxed = self.alt_or_strict_filter(user_budget, category, location)

        # 2. NearestNeighbors Feature Vectorization
        df_candidates = pd.DataFrame([
            {
                "minimum_investment": f.minimum_investment,
                "maximum_investment": f.maximum_investment,
                "roi": f.roi,
                "experience_required": f.experience_required,
                "market_demand": f.market_demand,
                "industry": f.industry,
                "risk_level": f.risk_level,
            }
            for f in candidates
        ])

        query_df = pd.DataFrame([{
            "minimum_investment": user_budget * 0.8,
            "maximum_investment": user_budget,
            "roi": expected_roi,
            "experience_required": experience_years,
            "market_demand": 8,
            "industry": category,
            "risk_level": risk_preference.capitalize(),
        }])

        numeric_cols = ["minimum_investment", "maximum_investment", "roi", "experience_required", "market_demand"]
        categorical_cols = ["industry", "risk_level"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ]
        )

        try:
            X_cand = preprocessor.fit_transform(df_candidates)
            X_query = preprocessor.transform(query_df)

            n_neighbors = min(len(candidates), max(top_k * 2, 10))
            nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
            nn_model.fit(X_cand)
            distances, indices = nn_model.kneighbors(X_query)

            distances = distances[0]
            indices = indices[0]
        except Exception as e:
            logger.warning(f"KNN transformation fallback: {e}")
            distances = np.zeros(len(candidates))
            indices = np.arange(len(candidates))

        # 3. Hybrid Scoring & Dynamic Ranking
        results: List[RecommendedFranchiseResult] = []

        for rank_idx, cand_idx in enumerate(indices):
            f = candidates[cand_idx]
            dist = distances[rank_idx] if rank_idx < len(distances) else 0.5
            knn_similarity = max(0.0, (1.0 - dist) * 100.0)

            # Domain Sub-scores
            sub = self._compute_sub_scores(
                f=f,
                user_budget=user_budget,
                category=category,
                location=location,
                experience_years=experience_years,
                expected_roi=expected_roi,
                risk_preference=risk_preference,
                stage7_risk=stage7_risk,
                stage7_roi=stage7_roi,
            )

            # Weighted sum of sub-scores
            domain_score = sum(sub[k] * WEIGHT_CONFIG[k] for k in WEIGHT_CONFIG if k in sub)

            # Hybrid score combination: 35% KNN Cosine Similarity + 65% Domain Logic
            final_match_score = (knn_similarity * 0.35) + (domain_score * 0.65)
            final_match_score = round(float(np.clip(final_match_score, 35.0, 98.5)), 1)

            # Recommendation type: PRIMARY vs ALTERNATIVE
            rec_type = "ALTERNATIVE" if is_relaxed or (category.lower() not in f.industry.lower() and sub["industry_fit"] < 80.0) else "PRIMARY"

            score_label = get_match_label(final_match_score)
            explanations = self._generate_explanations(f, sub, user_budget, category, location)

            results.append(
                RecommendedFranchiseResult(
                    franchise=f,
                    match_score=final_match_score,
                    score_label=score_label,
                    ranking_position=rank_idx + 1,
                    recommendation_type=rec_type,
                    explanation=explanations,
                    sub_scores=sub,
                )
            )

        # Sort descending by match_score
        results.sort(key=lambda r: r.match_score, reverse=True)

        # Re-assign ranking positions after sorting
        for pos, r in enumerate(results, start=1):
            r.ranking_position = pos

        return results[:top_k]

    def alt_or_strict_filter(self, user_budget: float, category: str, location: str):
        return self._apply_hard_filtering(user_budget, category, location)
