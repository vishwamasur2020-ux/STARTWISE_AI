"""
STARTWISE AI — Business Score Calculator (Stage 6)

Transparent, rule-based business scoring system (0–100).
This is intentionally SEPARATE from ML models so the formula can be
adjusted without retraining.

Scoring Formula:
    score = (
        0.40 * success_probability +      # 40% — ML model output
        0.25 * financial_health_score +   # 25% — profit margin based
        0.20 * market_opportunity_score + # 20% — demand based
        0.15 * experience_factor          # 15% — years experience
        - risk_penalty                    # subtracted for risk
        - competition_penalty             # subtracted for competition
    )

Risk Penalty:     Low=0,  Medium=10, High=25
Competition Penalty: Low=0, Medium=5, High=15

The score is clamped to [0, 100].

Academic Note:
    This hybrid approach (ML + rule-based scoring) is common in business
    intelligence systems. Pure ML scoring would make the formula a black box,
    which is unsuitable for explaining results to investors or validating logic.
"""

from __future__ import annotations

import numpy as np


# ── Penalty Tables ────────────────────────────────────────────────────────────
RISK_PENALTY = {"Low": 0, "Medium": 10, "High": 25}
COMPETITION_PENALTY = {"Low": 0, "Medium": 5, "High": 15}

# ── Score Weights ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "success_probability": 0.40,
    "financial_health": 0.25,
    "market_opportunity": 0.20,
    "experience_factor": 0.15,
}


def calculate_business_score(
    success_probability: float,          # 0..100 (from ML model)
    risk_level: str,                     # "Low" | "Medium" | "High"
    competition_level: str,              # "Low" | "Medium" | "High"
    profit_margin: float,                # -1..1
    market_demand: int,                  # 1..10
    experience_years: int,               # 0..25
    revenue_to_expense_ratio: float,     # 0..10
) -> float:
    """
    Calculate the overall Business Score (0–100).

    Args:
        success_probability: Success probability percentage (0–100)
        risk_level: "Low", "Medium", or "High"
        competition_level: "Low", "Medium", or "High"
        profit_margin: Profit margin ratio (-1 to 1)
        market_demand: Market demand score (1–10)
        experience_years: Founder experience in years
        revenue_to_expense_ratio: Revenue divided by expenses

    Returns:
        float: Business score clamped to [0, 100]
    """
    # ── Component 1: Success Probability (0..100) ─────────────────────────────
    success_component = float(success_probability)  # already 0..100

    # ── Component 2: Financial Health Score (0..100) ──────────────────────────
    # Derived from profit margin and revenue/expense ratio
    pm_norm = np.clip((profit_margin + 1) / 2, 0, 1)           # -1..1 → 0..1
    re_norm = np.clip(revenue_to_expense_ratio / 3.0, 0, 1)     # 0..3  → 0..1
    financial_health = float(np.clip((0.6 * pm_norm + 0.4 * re_norm) * 100, 0, 100))

    # ── Component 3: Market Opportunity Score (0..100) ────────────────────────
    demand_norm = (market_demand - 1) / 9.0  # 0..1
    market_opp = float(np.clip(demand_norm * 100, 0, 100))

    # ── Component 4: Experience Factor (0..100) ───────────────────────────────
    exp_score = float(np.clip((np.log1p(experience_years) / np.log1p(25)) * 100, 0, 100))

    # ── Penalties ─────────────────────────────────────────────────────────────
    risk_pen = RISK_PENALTY.get(risk_level, RISK_PENALTY["Medium"])
    comp_pen = COMPETITION_PENALTY.get(competition_level, COMPETITION_PENALTY["Medium"])

    # ── Weighted Sum ──────────────────────────────────────────────────────────
    raw_score = (
        WEIGHTS["success_probability"] * success_component +
        WEIGHTS["financial_health"] * financial_health +
        WEIGHTS["market_opportunity"] * market_opp +
        WEIGHTS["experience_factor"] * exp_score
        - risk_pen
        - comp_pen
    )

    score = float(np.clip(raw_score, 0, 100))
    return round(score, 2)


def explain_score(
    success_probability: float,
    risk_level: str,
    competition_level: str,
    profit_margin: float,
    market_demand: int,
    experience_years: int,
    revenue_to_expense_ratio: float,
) -> dict:
    """
    Return a breakdown of the business score for transparency.
    """
    pm_norm = float(np.clip((profit_margin + 1) / 2, 0, 1))
    re_norm = float(np.clip(revenue_to_expense_ratio / 3.0, 0, 1))
    financial_health = float(np.clip((0.6 * pm_norm + 0.4 * re_norm) * 100, 0, 100))
    market_opp = float(np.clip(((market_demand - 1) / 9.0) * 100, 0, 100))
    exp_score = float(np.clip((np.log1p(experience_years) / np.log1p(25)) * 100, 0, 100))

    risk_pen = RISK_PENALTY.get(risk_level, 10)
    comp_pen = COMPETITION_PENALTY.get(competition_level, 5)
    total = calculate_business_score(
        success_probability, risk_level, competition_level,
        profit_margin, market_demand, experience_years, revenue_to_expense_ratio
    )

    return {
        "total_score": total,
        "components": {
            "success_contribution": round(WEIGHTS["success_probability"] * success_probability, 2),
            "financial_health_contribution": round(WEIGHTS["financial_health"] * financial_health, 2),
            "market_opportunity_contribution": round(WEIGHTS["market_opportunity"] * market_opp, 2),
            "experience_contribution": round(WEIGHTS["experience_factor"] * exp_score, 2),
        },
        "penalties": {
            "risk_penalty": risk_pen,
            "competition_penalty": comp_pen,
        },
        "raw_components": {
            "success_probability": round(success_probability, 2),
            "financial_health_score": round(financial_health, 2),
            "market_opportunity_score": round(market_opp, 2),
            "experience_score": round(exp_score, 2),
        }
    }
