"""
STARTWISE AI — Data Preprocessing (Stage 6)

Handles:
  1. Dataset Validation — no nulls, valid ranges, no duplicates
  2. Data Cleaning — outlier handling, type coercion
  3. Feature/Target Separation — avoids target leakage
  4. Train/Test Split — 80/20, stratified where applicable
  5. ColumnTransformer Pipeline — OHE for categoricals, StandardScaler for numericals
     IMPORTANT: Preprocessor is fit ONLY on X_train to prevent data leakage.

Design:
  Each model gets its own preprocessor instance because:
  - Different target variables require different feature sets
  - Risk model excludes competition_level (could be correlated leak)
  - Competition model excludes risk_level for same reason
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from ml.ml_config import (
    RANDOM_STATE, TEST_SIZE, ALL_TARGETS,
    ENGINEERED_NUMERIC_COLS, ENGINEERED_CATEGORICAL_COLS,
    RISK_LEVELS, COMPETITION_LEVELS,
)


# ── Validation ───────────────────────────────────────────────────────────────

def validate_dataset(df: pd.DataFrame) -> bool:
    """
    Validate dataset before training.
    Raises ValueError if validation fails.

    Checks:
      - Minimum row count
      - No unexpected nulls in key columns
      - No duplicate rows
      - Positive investment_amount
      - Non-negative revenue and expenses
      - Valid numeric ranges for market_demand (1-10)
      - Valid categorical values for risk_level, competition_level
      - ROI in realistic range
    """
    print("[Preprocessing] Validating dataset...")
    errors = []

    # Row count check
    if len(df) < 100:
        errors.append(f"Dataset too small: {len(df)} rows (need at least 100)")

    # Null check on critical columns
    critical_cols = [
        "business_category", "investment_amount", "expected_monthly_revenue",
        "expected_monthly_expenses", "market_demand", "experience_years",
        "employee_count", "competition_level", "risk_level", "success", "roi"
    ]
    available_cols = [c for c in critical_cols if c in df.columns]
    null_counts = df[available_cols].isnull().sum()
    if null_counts.any():
        errors.append(f"Null values found:\n{null_counts[null_counts > 0]}")

    # Duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"[Preprocessing] Warning: {dup_count} duplicate rows found (will be dropped).")

    # investment_amount > 0
    if "investment_amount" in df.columns:
        bad_investment = (df["investment_amount"] <= 0).sum()
        if bad_investment > 0:
            errors.append(f"{bad_investment} rows have investment_amount <= 0")

    # Revenue and expenses >= 0
    for col in ["expected_monthly_revenue", "expected_monthly_expenses"]:
        if col in df.columns:
            bad = (df[col] < 0).sum()
            if bad > 0:
                errors.append(f"{bad} rows have {col} < 0")

    # market_demand 1–10
    if "market_demand" in df.columns:
        out_range = ((df["market_demand"] < 1) | (df["market_demand"] > 10)).sum()
        if out_range > 0:
            errors.append(f"{out_range} rows have market_demand outside [1, 10]")

    # experience_years >= 0
    if "experience_years" in df.columns:
        bad_exp = (df["experience_years"] < 0).sum()
        if bad_exp > 0:
            errors.append(f"{bad_exp} rows have experience_years < 0")

    # employee_count >= 0
    if "employee_count" in df.columns:
        bad_emp = (df["employee_count"] < 0).sum()
        if bad_emp > 0:
            errors.append(f"{bad_emp} rows have employee_count < 0")

    # Valid risk/competition levels
    if "risk_level" in df.columns:
        invalid_risk = ~df["risk_level"].isin(RISK_LEVELS)
        if invalid_risk.any():
            errors.append(f"{invalid_risk.sum()} rows have invalid risk_level")

    if "competition_level" in df.columns:
        invalid_comp = ~df["competition_level"].isin(COMPETITION_LEVELS)
        if invalid_comp.any():
            errors.append(f"{invalid_comp.sum()} rows have invalid competition_level")

    # ROI reasonable range
    if "roi" in df.columns:
        extreme_roi = ((df["roi"] < -100) | (df["roi"] > 500)).sum()
        if extreme_roi > 0:
            print(f"[Preprocessing] Warning: {extreme_roi} rows have extreme ROI values (outside -100..500)")

    if errors:
        msg = "\n".join(errors)
        raise ValueError(f"[Preprocessing] Dataset validation FAILED:\n{msg}")

    print(f"[Preprocessing] Validation PASSED — {len(df)} rows, {len(df.columns)} columns.")
    return True


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset:
      - Drop exact duplicates
      - Clip outliers in numeric cols using IQR
      - Ensure correct dtypes
    """
    original_len = len(df)
    df = df.drop_duplicates()
    dropped = original_len - len(df)
    if dropped > 0:
        print(f"[Preprocessing] Dropped {dropped} duplicate rows.")

    # IQR-based outlier clipping for investment / revenue / expenses
    for col in ["investment_amount", "expected_monthly_revenue", "expected_monthly_expenses"]:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.01)
        Q3 = df[col].quantile(0.99)
        df[col] = df[col].clip(lower=Q1, upper=Q3)

    # Ensure correct types
    int_cols = ["employee_count", "experience_years", "market_demand", "business_age", "success"]
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)

    float_cols = ["investment_amount", "expected_monthly_revenue", "expected_monthly_expenses",
                  "roi", "business_score", "profit_estimate"]
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)

    print(f"[Preprocessing] Cleaned dataset: {len(df)} rows remaining.")
    return df.reset_index(drop=True)


# ── Feature / Target Split ────────────────────────────────────────────────────

def get_features_and_target(
    df: pd.DataFrame,
    target: str,
    exclude_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separate features (X) from target (y).

    IMPORTANT:
        All target columns are always excluded from X to prevent target leakage.
        Additional columns can be excluded via exclude_cols.
    """
    always_exclude = list(ALL_TARGETS)
    if exclude_cols:
        always_exclude += exclude_cols

    feature_cols = [c for c in df.columns if c not in always_exclude]
    X = df[feature_cols].copy()
    y = df[target].copy()
    return X, y


# ── ColumnTransformer Pipeline ────────────────────────────────────────────────

def build_preprocessor(
    numeric_cols: List[str],
    categorical_cols: List[str],
) -> ColumnTransformer:
    """
    Build a ColumnTransformer that:
      - Imputes then scales numeric columns
      - Imputes then one-hot-encodes categorical columns

    The transformer is NOT fit here — it will be fit on X_train only.
    """
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    transformer = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return transformer


def prepare_data(
    df: pd.DataFrame,
    target: str,
    numeric_cols: List[str],
    categorical_cols: List[str],
    exclude_cols: Optional[List[str]] = None,
    stratify: bool = False,
) -> Tuple:
    """
    Full preparation pipeline:
      1. Feature/target split
      2. Train/test split (80/20)
      3. Build ColumnTransformer
      4. Fit on X_train ONLY, transform both X_train and X_test

    Returns:
        X_train_t, X_test_t, y_train, y_test, preprocessor, feature_names
    """
    X, y = get_features_and_target(df, target, exclude_cols)

    # Ensure only available columns are used
    available_numeric = [c for c in numeric_cols if c in X.columns]
    available_categorical = [c for c in categorical_cols if c in X.columns]

    print(f"[Preprocessing] Target: '{target}' | Features: {len(available_numeric)} numeric, {len(available_categorical)} categorical")

    # Train/test split
    split_kwargs = dict(test_size=TEST_SIZE, random_state=RANDOM_STATE)
    if stratify:
        split_kwargs["stratify"] = y

    X_train, X_test, y_train, y_test = train_test_split(X, y, **split_kwargs)
    print(f"[Preprocessing] Train: {len(X_train)}, Test: {len(X_test)}")

    # Build and fit preprocessor on TRAINING data only
    preprocessor = build_preprocessor(available_numeric, available_categorical)
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    # Get feature names after OHE
    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = [f"feature_{i}" for i in range(X_train_t.shape[1])]

    print(f"[Preprocessing] Transformed features: {len(feature_names)}")
    return X_train_t, X_test_t, y_train, y_test, preprocessor, feature_names
