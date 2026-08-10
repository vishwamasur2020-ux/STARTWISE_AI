"""
STARTWISE AI — Synthetic Dataset Generator (Stage 6)

Generates a realistic 5,000-record dataset for startup/business validation.
The dataset contains intentional statistical correlations that mirror real-world
business fundamentals, making it appropriate for training ML classifiers and regressors.

DISCLAIMER:
    This is a SYNTHETIC dataset created for demonstration and academic purposes.
    It does NOT represent real-world proprietary business data and should NOT be
    used to make actual financial or business decisions.

Dataset Fields:
    - business_category, business_model, investment_amount
    - expected_monthly_revenue, expected_monthly_expenses
    - employee_count, experience_years, location
    - target_customer, market_demand, competition_level
    - funding_source, business_age
    - [Targets] success, roi, risk_level, business_score

Realistic Correlations Baked In:
    - High market_demand + reasonable investment + low competition + more experience → success=1
    - High expenses + low demand + high competition + less experience → risk=High
    - ROI is derived from financial variables (revenue/expense/investment ratios)
    - Business score combines multiple factors
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Allow running as standalone script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.ml_config import (
    RANDOM_STATE, NUM_SAMPLES, RAW_DATASET_PATH,
    BUSINESS_CATEGORIES, BUSINESS_MODELS, LOCATIONS,
    TARGET_CUSTOMERS, FUNDING_SOURCES, DATASET_VERSION,
)


def generate_dataset(n_samples: int = NUM_SAMPLES, seed: int = RANDOM_STATE) -> pd.DataFrame:
    """
    Generate a realistic synthetic dataset for startup/business validation.

    Args:
        n_samples: Number of records to generate (default: 5000)
        seed: Random seed for reproducibility (default: 42)

    Returns:
        pd.DataFrame: Generated dataset
    """
    rng = np.random.default_rng(seed)

    print(f"[DatasetGenerator] Generating {n_samples} records (seed={seed})...")

    # ── Category & Model Mapping ──────────────────────────────────────────────
    CATEGORY_MODEL_MAP = {
        "Food":           ["Cafe", "Restaurant", "Food Delivery", "Catering"],
        "Retail":         ["Online Store", "General Store", "Franchise", "Boutique"],
        "Technology":     ["SaaS", "Mobile App", "IT Services", "E-Commerce"],
        "Healthcare":     ["Clinic", "Pharmacy", "Diagnostic Lab", "Wellness Center"],
        "Education":      ["Tuition Center", "School", "Online Coaching", "Skill Training"],
        "Agriculture":    ["Farm", "Agro Processing", "Organic Produce", "Dairy"],
        "Manufacturing":  ["Factory", "Workshop", "Handloom", "Auto Parts"],
        "Finance":        ["Investment Advisory", "Insurance Agency", "Microfinance", "Forex"],
        "Tourism":        ["Hotel", "Resort", "Travel Agency", "Adventure Sports"],
        "Other":          ["Consulting", "Event Management", "Real Estate", "Logistics"],
    }

    # ── Market Demand Weights by Category ────────────────────────────────────
    # Some categories naturally have higher demand
    CATEGORY_DEMAND_MEAN = {
        "Technology": 7.5, "Healthcare": 7.0, "Education": 6.8,
        "Food": 6.5, "Finance": 6.2, "Retail": 6.0,
        "Tourism": 5.8, "Agriculture": 5.5, "Manufacturing": 5.2, "Other": 5.0,
    }

    # ── Investment Range by Category (in INR thousands) ──────────────────────
    CATEGORY_INVESTMENT_RANGE = {
        "Technology":     (200_000,  2_000_000),
        "Healthcare":     (500_000,  5_000_000),
        "Manufacturing":  (500_000,  5_000_000),
        "Finance":        (300_000,  3_000_000),
        "Tourism":        (800_000, 10_000_000),
        "Education":      (100_000,  1_500_000),
        "Food":           ( 50_000,    800_000),
        "Retail":         (100_000,  2_000_000),
        "Agriculture":    ( 50_000,    500_000),
        "Other":          (100_000,  2_000_000),
    }

    # ── Base Revenue Multiplier by Category ───────────────────────────────────
    CATEGORY_REVENUE_MULT = {
        "Technology": 0.12, "Finance": 0.10, "Healthcare": 0.09,
        "Tourism": 0.08, "Education": 0.08, "Manufacturing": 0.07,
        "Food": 0.15, "Retail": 0.13, "Agriculture": 0.11, "Other": 0.09,
    }

    # ── Expense Ratio by Category (expenses / revenue) ────────────────────────
    CATEGORY_EXPENSE_RATIO = {
        "Food": 0.68, "Retail": 0.72, "Manufacturing": 0.75,
        "Technology": 0.55, "Healthcare": 0.65, "Education": 0.58,
        "Finance": 0.50, "Tourism": 0.70, "Agriculture": 0.65, "Other": 0.65,
    }

    # ── Generate Base Features ─────────────────────────────────────────────────
    business_categories = rng.choice(BUSINESS_CATEGORIES, size=n_samples,
                                      p=[0.15, 0.12, 0.18, 0.10, 0.10,
                                         0.07, 0.07, 0.08, 0.08, 0.05])

    business_models = [
        rng.choice(CATEGORY_MODEL_MAP[cat]) for cat in business_categories
    ]

    locations = rng.choice(LOCATIONS, size=n_samples,
                           p=[0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.07, 0.05, 0.03, 0.02])

    target_customers = rng.choice(TARGET_CUSTOMERS, size=n_samples)
    funding_sources = rng.choice(FUNDING_SOURCES, size=n_samples,
                                  p=[0.35, 0.30, 0.12, 0.08, 0.05, 0.07, 0.03])
    experience_years = np.clip(rng.negative_binomial(3, 0.3, n_samples), 0, 25)
    employee_count = np.clip(rng.negative_binomial(2, 0.25, n_samples) + 1, 1, 200)
    business_age = rng.integers(0, 11, size=n_samples)

    # Investment amount (category-aware)
    investment_amount = np.zeros(n_samples)
    for i, cat in enumerate(business_categories):
        lo, hi = CATEGORY_INVESTMENT_RANGE[cat]
        investment_amount[i] = rng.integers(lo, hi + 1)

    # Market demand (category-aware with noise)
    market_demand = np.zeros(n_samples, dtype=int)
    for i, cat in enumerate(business_categories):
        mean_d = CATEGORY_DEMAND_MEAN[cat]
        raw = rng.normal(mean_d, 1.5)
        market_demand[i] = int(np.clip(round(raw), 1, 10))

    # Revenue (investment * multiplier * demand factor * experience boost * noise)
    expected_monthly_revenue = np.zeros(n_samples)
    expected_monthly_expenses = np.zeros(n_samples)

    for i, cat in enumerate(business_categories):
        mult = CATEGORY_REVENUE_MULT[cat]
        demand_factor = 0.7 + 0.06 * market_demand[i]         # demand 1→0.76, demand 10→1.3
        exp_boost = 1.0 + 0.03 * min(experience_years[i], 15)  # +3% per year up to 15yr
        emp_factor = 1.0 + 0.005 * min(employee_count[i], 50)  # +0.5% per employee up to 50
        noise = rng.normal(1.0, 0.20)

        revenue = investment_amount[i] * mult * demand_factor * exp_boost * emp_factor * noise
        expected_monthly_revenue[i] = max(revenue, 0)

        exp_ratio = CATEGORY_EXPENSE_RATIO[cat]
        exp_noise = rng.normal(1.0, 0.12)
        expenses = expected_monthly_revenue[i] * exp_ratio * exp_noise
        expected_monthly_expenses[i] = max(expenses, 0)

    # ── Derived Profit ────────────────────────────────────────────────────────
    profit_estimate = expected_monthly_revenue - expected_monthly_expenses
    profit_margin = np.where(
        expected_monthly_revenue > 0,
        profit_estimate / expected_monthly_revenue,
        0.0
    )

    # ── Competition Level (deterministic with noise) ──────────────────────────
    # High-demand categories attract more competition
    competition_score_raw = np.zeros(n_samples)
    for i, cat in enumerate(business_categories):
        base = CATEGORY_DEMAND_MEAN[cat] / 10.0  # 0..1
        urban_boost = 0.1 if locations[i] in ["Bengaluru", "Mumbai", "Delhi"] else 0.0
        exp_boost_c = -0.02 * experience_years[i]  # More experience → can navigate competition
        noise_c = rng.normal(0, 0.1)
        competition_score_raw[i] = np.clip(base + urban_boost + exp_boost_c + noise_c, 0, 1)

    competition_thresholds = (0.35, 0.65)
    competition_levels = np.where(
        competition_score_raw < competition_thresholds[0], "Low",
        np.where(competition_score_raw < competition_thresholds[1], "Medium", "High")
    )

    # ── SUCCESS Probability Score (0..1) ─────────────────────────────────────
    # Factors: profit_margin, market_demand, experience, competition, funding
    funding_bonus = {
        "VC": 0.12, "Angel Investor": 0.08, "Government Grant": 0.05,
        "Bank Loan": 0.02, "Personal": 0.00, "Friends & Family": 0.01,
        "Crowdfunding": 0.03,
    }

    success_score = np.zeros(n_samples)
    for i in range(n_samples):
        pm = np.clip(profit_margin[i], -0.5, 0.8)                  # profit margin contribution
        dm = (market_demand[i] - 1) / 9.0                           # 0..1
        exp_s = min(experience_years[i] / 15.0, 1.0)                # 0..1
        comp_pen = {"Low": 0.0, "Medium": -0.05, "High": -0.15}[competition_levels[i]]
        fund_b = funding_bonus.get(funding_sources[i], 0.0)
        age_b = min(business_age[i] / 10.0, 0.1)

        raw_score = (
            0.35 * (pm + 0.5) / 1.3 +   # normalized profit margin
            0.25 * dm +
            0.20 * exp_s +
            0.10 * (employee_count[i] / 200.0) +
            comp_pen + fund_b + age_b
        )
        noise_s = rng.normal(0, 0.07)
        success_score[i] = np.clip(raw_score + noise_s, 0, 1)

    success = (success_score > 0.52).astype(int)

    # ── ROI Calculation ────────────────────────────────────────────────────────
    # Annual ROI % = (Annual Profit / Investment) * 100
    annual_profit = profit_estimate * 12
    roi_raw = np.where(
        investment_amount > 0,
        (annual_profit / investment_amount) * 100,
        0.0
    )
    roi_noise = rng.normal(0, 5, n_samples)
    roi = np.clip(roi_raw + roi_noise, -50, 200)  # cap to realistic range

    # ── Risk Level ────────────────────────────────────────────────────────────
    # Risk derives from: low profit margin + high expenses + low experience + low demand
    risk_score = np.zeros(n_samples)
    for i in range(n_samples):
        pm = profit_margin[i]
        low_margin_pen = max(0, -pm) * 0.4           # negative margin increases risk
        low_exp_pen = max(0, 0.5 - experience_years[i] / 15.0) * 0.2
        high_comp_pen = {"Low": 0.0, "Medium": 0.1, "High": 0.25}[competition_levels[i]]
        low_demand_pen = max(0, 0.5 - (market_demand[i] - 1) / 9.0) * 0.2
        high_invest_pen = max(0, investment_amount[i] / 5_000_000 - 0.5) * 0.1

        noise_r = rng.normal(0, 0.06)
        risk_score[i] = np.clip(
            low_margin_pen + low_exp_pen + high_comp_pen + low_demand_pen + high_invest_pen + noise_r,
            0, 1
        )

    risk_thresholds = (0.25, 0.55)
    risk_levels = np.where(
        risk_score < risk_thresholds[0], "Low",
        np.where(risk_score < risk_thresholds[1], "Medium", "High")
    )

    # ── Business Score (0–100) ────────────────────────────────────────────────
    # Combines: success probability, financial health, market opportunity
    # Penalizes: high risk, high competition
    RISK_PENALTY_MAP = {"Low": 0, "Medium": 10, "High": 25}
    COMP_PENALTY_MAP = {"Low": 0, "Medium": 5, "High": 15}

    business_score = np.zeros(n_samples)
    for i in range(n_samples):
        # Financial health (0–100)
        fin_health = np.clip(50 + profit_margin[i] * 100, 0, 100)
        # Market opportunity (0–100)
        mkt_opp = (market_demand[i] - 1) / 9.0 * 100
        # Risk and competition penalties
        risk_pen = RISK_PENALTY_MAP[risk_levels[i]]
        comp_pen = COMP_PENALTY_MAP[competition_levels[i]]

        raw_bs = (
            0.40 * success_score[i] * 100 +
            0.25 * fin_health +
            0.20 * mkt_opp +
            0.15 * (experience_years[i] / 25.0 * 100)
            - risk_pen - comp_pen
        )
        noise_bs = rng.normal(0, 3)
        business_score[i] = np.clip(raw_bs + noise_bs, 0, 100)

    # ── Assemble DataFrame ────────────────────────────────────────────────────
    df = pd.DataFrame({
        "business_category":        business_categories,
        "business_model":           business_models,
        "investment_amount":        investment_amount.astype(int),
        "expected_monthly_revenue": np.round(expected_monthly_revenue, 2),
        "expected_monthly_expenses": np.round(expected_monthly_expenses, 2),
        "profit_estimate":          np.round(profit_estimate, 2),
        "employee_count":           employee_count.astype(int),
        "experience_years":         experience_years.astype(int),
        "location":                 locations,
        "target_customer":          target_customers,
        "market_demand":            market_demand.astype(int),
        "competition_level":        competition_levels,
        "funding_source":           funding_sources,
        "business_age":             business_age.astype(int),
        # Targets
        "success":                  success.astype(int),
        "roi":                      np.round(roi, 2),
        "risk_level":               risk_levels,
        "business_score":           np.round(business_score, 2),
    })

    print(f"[DatasetGenerator] Generated {len(df)} records.")
    print(f"[DatasetGenerator] Success rate: {df['success'].mean():.1%}")
    print(f"[DatasetGenerator] Risk distribution: {df['risk_level'].value_counts().to_dict()}")
    print(f"[DatasetGenerator] Competition distribution: {df['competition_level'].value_counts().to_dict()}")
    print(f"[DatasetGenerator] ROI range: [{df['roi'].min():.1f}%, {df['roi'].max():.1f}%], mean={df['roi'].mean():.1f}%")

    return df


def save_dataset(df: pd.DataFrame, path: Path = RAW_DATASET_PATH) -> None:
    """Save dataset to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[DatasetGenerator] Saved to: {path}")


def load_dataset(path: Path = RAW_DATASET_PATH) -> pd.DataFrame:
    """Load dataset from CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Run generate_dataset() first.")
    df = pd.read_csv(path)
    print(f"[DatasetGenerator] Loaded {len(df)} records from: {path}")
    return df


if __name__ == "__main__":
    df = generate_dataset()
    save_dataset(df)
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
