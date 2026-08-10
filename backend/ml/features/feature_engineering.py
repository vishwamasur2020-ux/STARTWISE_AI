"""
STARTWISE AI — Feature Engineering (Stage 6)

Creates meaningful derived features from raw startup data.
These features improve model signal by capturing domain-relevant relationships.

IMPORTANT: Feature engineering is applied BEFORE the train/test split so that
           derived columns are available for the ColumnTransformer.
           However, the ColumnTransformer (scaler/encoder) is still fit ONLY
           on training data, so there is no leakage.

Derived Features:
  - profit_estimate              : monthly_revenue - monthly_expenses
  - profit_margin                : profit / revenue (clamped to [-1, 1])
  - revenue_to_expense_ratio     : revenue / expenses (clamped)
  - investment_to_revenue_ratio  : annual_revenue / investment
  - experience_score             : log1p scaled experience (0..1)
  - market_opportunity_score     : composite of demand + experience (0..100)
  - competition_score_num        : numeric encoding of competition_level
  - financial_health_score       : composite financial metric (0..100)
  - customer_market_score        : demand * customer base proxy (0..1)
  - investment_category          : categorical bin (small/medium/large)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


COMPETITION_NUM_MAP = {"Low": 0, "Medium": 1, "High": 2}


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all derived/engineered features to the DataFrame in-place (returns new copy).

    Args:
        df: Raw or cleaned DataFrame with at least the base columns present.

    Returns:
        pd.DataFrame: DataFrame with additional engineered feature columns appended.
    """
    df = df.copy()

    rev = df["expected_monthly_revenue"].values
    exp = df["expected_monthly_expenses"].values
    inv = df["investment_amount"].values
    demand = df["market_demand"].values
    experience = df["experience_years"].values
    employees = df["employee_count"].values

    # ── 1. Profit Estimate ────────────────────────────────────────────────────
    if "profit_estimate" not in df.columns:
        df["profit_estimate"] = rev - exp

    profit = df["profit_estimate"].values

    # ── 2. Profit Margin ──────────────────────────────────────────────────────
    with np.errstate(divide="ignore", invalid="ignore"):
        raw_pm = np.where(rev > 0, profit / rev, 0.0)
    df["profit_margin"] = np.clip(raw_pm, -1.0, 1.0)

    # ── 3. Revenue-to-Expense Ratio ───────────────────────────────────────────
    with np.errstate(divide="ignore", invalid="ignore"):
        rev_exp = np.where(exp > 0, rev / exp, 2.0)  # 2.0 = "very healthy"
    df["revenue_to_expense_ratio"] = np.clip(rev_exp, 0, 10)

    # ── 4. Investment-to-Revenue Ratio ────────────────────────────────────────
    # Annual revenue / investment — how quickly investment pays back
    annual_rev = rev * 12
    with np.errstate(divide="ignore", invalid="ignore"):
        inv_rev = np.where(inv > 0, annual_rev / inv, 0.0)
    df["investment_to_revenue_ratio"] = np.clip(inv_rev, 0, 20)

    # ── 5. Experience Score (log-scaled 0..1) ─────────────────────────────────
    # log1p gives diminishing returns — going from 0→1yr more impactful than 14→15yr
    df["experience_score"] = np.log1p(experience) / np.log1p(25)

    # ── 6. Market Opportunity Score (0..100) ─────────────────────────────────
    # Combines demand (1–10) and experience (0..25) into a 0–100 score
    demand_norm = (demand - 1) / 9.0      # 0..1
    exp_norm = np.log1p(experience) / np.log1p(25)  # 0..1
    df["market_opportunity_score"] = np.clip(
        (0.7 * demand_norm + 0.3 * exp_norm) * 100, 0, 100
    )

    # ── 7. Competition Score (numeric encoding) ───────────────────────────────
    if "competition_level" in df.columns:
        df["competition_score_num"] = df["competition_level"].map(COMPETITION_NUM_MAP).fillna(1).astype(int)
    else:
        df["competition_score_num"] = 1  # default medium

    # ── 8. Financial Health Score (0..100) ────────────────────────────────────
    # Based on profit margin + revenue-to-expense ratio
    pm_norm = np.clip((df["profit_margin"].values + 1) / 2, 0, 1)       # -1..1 → 0..1
    re_norm = np.clip(df["revenue_to_expense_ratio"].values / 3.0, 0, 1)  # 0..3 → 0..1
    df["financial_health_score"] = np.clip(
        (0.6 * pm_norm + 0.4 * re_norm) * 100, 0, 100
    )

    # ── 9. Customer Market Score (0..1) ───────────────────────────────────────
    # Demand × employee capacity proxy
    emp_norm = np.log1p(employees) / np.log1p(200)  # 0..1
    df["customer_market_score"] = np.clip(
        0.6 * demand_norm + 0.4 * emp_norm, 0, 1
    )

    # ── 10. Investment Category (categorical) ─────────────────────────────────
    inv_arr = df["investment_amount"].values
    investment_category = np.where(
        inv_arr < 200_000, "Small",
        np.where(inv_arr < 1_000_000, "Medium", "Large")
    )
    df["investment_category"] = investment_category

    return df


def get_feature_names_for_model(model_name: str) -> tuple[list, list]:
    """
    Return (numeric_cols, categorical_cols) for each model's feature set.
    Targets are never included here (they are removed in preprocessing step).

    Model-specific exclusions:
      - success model: does not use risk_level / competition_level as features
      - risk model: does not use success / competition_level as features
      - roi model: does not use success / risk_level / competition_level as features
      - competition model: does not use success / risk_level as features
    """
    numeric_base = [
        "investment_amount",
        "expected_monthly_revenue",
        "expected_monthly_expenses",
        "employee_count",
        "experience_years",
        "market_demand",
        "business_age",
        "profit_estimate",
        "profit_margin",
        "revenue_to_expense_ratio",
        "investment_to_revenue_ratio",
        "experience_score",
        "market_opportunity_score",
        "financial_health_score",
        "customer_market_score",
    ]

    categorical_base = [
        "business_category",
        "business_model",
        "location",
        "target_customer",
        "funding_source",
        "investment_category",
    ]

    # competition_score_num is excluded for competition model (it IS the target numerically)
    # Include it for success, risk, roi models as it's an important signal
    if model_name in ("success", "risk", "roi"):
        numeric_base = numeric_base + ["competition_score_num"]

    return numeric_base, categorical_base
