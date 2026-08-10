"""
STARTWISE AI — ML Configuration (Stage 6)
Central configuration for all ML components:
  - Paths and directories
  - Random seed for reproducibility
  - Feature definitions per model
  - Hyperparameters
  - Target variables
  - Dataset settings
"""

import os
from pathlib import Path

# ── Base Paths ────────────────────────────────────────────────────────────────
ML_BASE = Path(__file__).resolve().parent
BACKEND_BASE = ML_BASE.parent

# Data directories
DATA_DIR = ML_BASE / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Artifact directories
ARTIFACTS_DIR = ML_BASE / "artifacts"
PLOTS_DIR = ARTIFACTS_DIR / "plots"

# Create required directories if they don't exist
for _dir in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ARTIFACTS_DIR, PLOTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ── File Paths ────────────────────────────────────────────────────────────────
RAW_DATASET_PATH = RAW_DATA_DIR / "startwise_dataset.csv"
PROCESSED_DATASET_PATH = PROCESSED_DATA_DIR / "startwise_clean.csv"

# Model artifact paths
SUCCESS_MODEL_PATH = ARTIFACTS_DIR / "success_model.joblib"
RISK_MODEL_PATH = ARTIFACTS_DIR / "risk_model.joblib"
ROI_MODEL_PATH = ARTIFACTS_DIR / "roi_model.joblib"
COMPETITION_MODEL_PATH = ARTIFACTS_DIR / "competition_model.joblib"

# Preprocessor artifact paths
SUCCESS_PREPROCESSOR_PATH = ARTIFACTS_DIR / "success_preprocessor.joblib"
RISK_PREPROCESSOR_PATH = ARTIFACTS_DIR / "risk_preprocessor.joblib"
ROI_PREPROCESSOR_PATH = ARTIFACTS_DIR / "roi_preprocessor.joblib"
COMPETITION_PREPROCESSOR_PATH = ARTIFACTS_DIR / "competition_preprocessor.joblib"

# Metadata paths
FEATURE_METADATA_PATH = ARTIFACTS_DIR / "feature_metadata.json"
MODEL_METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_STATE = 42
DATASET_VERSION = "1.0.0"

# ── Dataset Settings ──────────────────────────────────────────────────────────
NUM_SAMPLES = 5000
TEST_SIZE = 0.2  # 80/20 train-test split

# ── Target Variables ──────────────────────────────────────────────────────────
TARGET_SUCCESS = "success"                    # Model 1: binary 0/1
TARGET_RISK = "risk_level"                   # Model 2: Low/Medium/High
TARGET_ROI = "roi"                           # Model 3: continuous float
TARGET_COMPETITION = "competition_level"     # Model 4: Low/Medium/High

ALL_TARGETS = [TARGET_SUCCESS, TARGET_RISK, TARGET_ROI, TARGET_COMPETITION, "business_score"]

# ── Categorical Feature Values ────────────────────────────────────────────────
BUSINESS_CATEGORIES = [
    "Food", "Retail", "Technology", "Healthcare", "Education",
    "Agriculture", "Manufacturing", "Finance", "Tourism", "Other"
]

BUSINESS_MODELS = [
    "Cafe", "Restaurant", "Online Store", "SaaS", "Mobile App",
    "Clinic", "Pharmacy", "Tuition Center", "School", "Farm",
    "Agro Processing", "Factory", "Workshop", "Investment Advisory",
    "Hotel", "Resort", "Travel Agency", "General Store", "Franchise", "Other"
]

LOCATIONS = [
    "Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Rural"
]

TARGET_CUSTOMERS = [
    "Students", "Families", "Professionals", "Businesses",
    "Seniors", "Youth", "General Public", "Women", "Farmers"
]

FUNDING_SOURCES = [
    "Personal", "Bank Loan", "Angel Investor", "VC", "Government Grant",
    "Friends & Family", "Crowdfunding"
]

RISK_LEVELS = ["Low", "Medium", "High"]
COMPETITION_LEVELS = ["Low", "Medium", "High"]

# ── Raw Feature Columns (before feature engineering) ─────────────────────────
RAW_FEATURE_COLS = [
    "business_category",
    "business_model",
    "investment_amount",
    "expected_monthly_revenue",
    "expected_monthly_expenses",
    "employee_count",
    "experience_years",
    "location",
    "target_customer",
    "market_demand",
    "funding_source",
    "business_age",
]

# ── Engineered Feature Columns ────────────────────────────────────────────────
ENGINEERED_NUMERIC_COLS = [
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
    "competition_score_num",
    "financial_health_score",
    "customer_market_score",
]

ENGINEERED_CATEGORICAL_COLS = [
    "business_category",
    "business_model",
    "location",
    "target_customer",
    "funding_source",
    "investment_category",
]

# ── Hyperparameters ───────────────────────────────────────────────────────────
SUCCESS_MODEL_PARAMS = {
    "n_estimators": 200,
    "max_depth": 12,
    "min_samples_split": 10,
    "min_samples_leaf": 4,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
    "class_weight": "balanced",
}

RISK_MODEL_PARAMS = {
    "max_depth": 8,
    "min_samples_split": 10,
    "min_samples_leaf": 4,
    "random_state": RANDOM_STATE,
    "class_weight": "balanced",
}

ROI_MODEL_PARAMS = {
    # LinearRegression has no key hyperparameters
    "fit_intercept": True,
}

COMPETITION_MODEL_PARAMS = {
    "n_estimators": 150,
    "max_depth": 10,
    "min_samples_split": 8,
    "min_samples_leaf": 3,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
    "class_weight": "balanced",
}

# ── Business Score Weights ─────────────────────────────────────────────────────
# Score = w1*success_prob + w2*financial_health - w3*risk_penalty - w4*competition_penalty
SCORE_WEIGHTS = {
    "success_probability": 0.40,    # 40%
    "financial_health": 0.25,       # 25%
    "market_opportunity": 0.20,     # 20%
    "risk_penalty": 0.10,           # -10% for high risk
    "competition_penalty": 0.05,    # -5% for high competition
}

# Risk/Competition multipliers (penalty values)
RISK_PENALTY = {"Low": 0, "Medium": 10, "High": 25}
COMPETITION_PENALTY = {"Low": 0, "Medium": 5, "High": 15}
