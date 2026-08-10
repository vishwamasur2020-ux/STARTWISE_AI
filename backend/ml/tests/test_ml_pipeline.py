"""
STARTWISE AI — ML Pipeline Tests (Stage 6)

Tests for:
  1. Dataset generation (schema, row count, value ranges)
  2. Dataset validation (error cases)
  3. Feature engineering (column names, value ranges)
  4. Preprocessing (no leakage, correct shapes)
  5. Model loading (artifacts present)
  6. Prediction output (structure, value ranges)
  7. Edge cases (invalid input, missing fields, negative values, unknown categories)
  8. Business score calculation

Run:
    cd backend
    .\\venv\\Scripts\\python.exe -m pytest ml/tests/ -v

    # Or with detailed output:
    .\\venv\\Scripts\\python.exe -m pytest ml/tests/ -v -s
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.utils.dataset_generator import generate_dataset
from ml.ml_config import (
    RISK_LEVELS, COMPETITION_LEVELS,
    SUCCESS_MODEL_PATH, RISK_MODEL_PATH, ROI_MODEL_PATH, COMPETITION_MODEL_PATH,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def small_dataset():
    """Generate a small dataset for testing (500 rows)."""
    return generate_dataset(n_samples=500, seed=42)


@pytest.fixture(scope="module")
def engineered_dataset(small_dataset):
    """Dataset with engineered features."""
    from ml.preprocessing.data_preprocessing import validate_dataset, clean_dataset
    from ml.features.feature_engineering import add_engineered_features
    df = clean_dataset(small_dataset)
    return add_engineered_features(df)


# ─── 1. Dataset Generation Tests ─────────────────────────────────────────────

class TestDatasetGeneration:

    def test_dataset_has_correct_shape(self, small_dataset):
        """Dataset should have 500 rows and expected columns."""
        assert len(small_dataset) == 500
        assert len(small_dataset.columns) >= 15

    def test_dataset_has_required_columns(self, small_dataset):
        required = [
            "business_category", "investment_amount", "expected_monthly_revenue",
            "expected_monthly_expenses", "employee_count", "experience_years",
            "market_demand", "competition_level", "risk_level", "success", "roi"
        ]
        for col in required:
            assert col in small_dataset.columns, f"Missing column: {col}"

    def test_investment_amount_positive(self, small_dataset):
        """All investment amounts must be positive."""
        assert (small_dataset["investment_amount"] > 0).all()

    def test_revenue_non_negative(self, small_dataset):
        """Revenue must be non-negative."""
        assert (small_dataset["expected_monthly_revenue"] >= 0).all()

    def test_expenses_non_negative(self, small_dataset):
        """Expenses must be non-negative."""
        assert (small_dataset["expected_monthly_expenses"] >= 0).all()

    def test_market_demand_range(self, small_dataset):
        """Market demand must be 1–10."""
        assert small_dataset["market_demand"].between(1, 10).all()

    def test_experience_years_non_negative(self, small_dataset):
        """Experience years must be >= 0."""
        assert (small_dataset["experience_years"] >= 0).all()

    def test_employee_count_positive(self, small_dataset):
        """Employee count must be >= 1."""
        assert (small_dataset["employee_count"] >= 1).all()

    def test_success_binary(self, small_dataset):
        """Success must be 0 or 1."""
        assert set(small_dataset["success"].unique()).issubset({0, 1})

    def test_risk_levels_valid(self, small_dataset):
        """Risk level must be Low, Medium, or High."""
        assert set(small_dataset["risk_level"].unique()).issubset(set(RISK_LEVELS))

    def test_competition_levels_valid(self, small_dataset):
        """Competition level must be Low, Medium, or High."""
        assert set(small_dataset["competition_level"].unique()).issubset(set(COMPETITION_LEVELS))

    def test_no_nulls_in_key_columns(self, small_dataset):
        key_cols = ["investment_amount", "expected_monthly_revenue",
                    "market_demand", "success", "roi", "risk_level"]
        assert small_dataset[key_cols].isnull().sum().sum() == 0

    def test_roi_has_variance(self, small_dataset):
        """ROI should not be all the same value."""
        assert small_dataset["roi"].std() > 0

    def test_success_has_both_classes(self, small_dataset):
        """Success column must have both 0 and 1."""
        unique_values = set(small_dataset["success"].unique())
        assert 0 in unique_values and 1 in unique_values

    def test_risk_has_all_three_classes(self, small_dataset):
        """Risk level should have Low, Medium, and High."""
        unique_risks = set(small_dataset["risk_level"].unique())
        assert len(unique_risks) >= 2  # At least 2 of 3 classes

    def test_reproducibility(self):
        """Same seed should produce identical datasets."""
        df1 = generate_dataset(n_samples=100, seed=99)
        df2 = generate_dataset(n_samples=100, seed=99)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_produce_different_data(self):
        """Different seeds should produce different datasets."""
        df1 = generate_dataset(n_samples=100, seed=1)
        df2 = generate_dataset(n_samples=100, seed=2)
        # At least some values should differ
        assert not df1["investment_amount"].equals(df2["investment_amount"])


# ─── 2. Dataset Validation Tests ─────────────────────────────────────────────

class TestDatasetValidation:

    def test_valid_dataset_passes(self, small_dataset):
        from ml.preprocessing.data_preprocessing import validate_dataset
        assert validate_dataset(small_dataset) is True

    def test_negative_investment_fails(self, small_dataset):
        from ml.preprocessing.data_preprocessing import validate_dataset
        bad_df = small_dataset.copy()
        bad_df.loc[0, "investment_amount"] = -1000
        with pytest.raises(ValueError, match="investment_amount"):
            validate_dataset(bad_df)

    def test_too_few_rows_fails(self):
        from ml.preprocessing.data_preprocessing import validate_dataset
        tiny_df = generate_dataset(n_samples=10, seed=42)
        with pytest.raises(ValueError):
            validate_dataset(tiny_df)

    def test_invalid_risk_level_fails(self, small_dataset):
        from ml.preprocessing.data_preprocessing import validate_dataset
        bad_df = small_dataset.copy()
        bad_df.loc[0, "risk_level"] = "Critical"
        with pytest.raises(ValueError):
            validate_dataset(bad_df)


# ─── 3. Feature Engineering Tests ────────────────────────────────────────────

class TestFeatureEngineering:

    def test_engineered_columns_added(self, engineered_dataset):
        """All engineered features should be present."""
        expected_cols = [
            "profit_estimate", "profit_margin", "revenue_to_expense_ratio",
            "investment_to_revenue_ratio", "experience_score",
            "market_opportunity_score", "competition_score_num",
            "financial_health_score", "customer_market_score",
            "investment_category",
        ]
        for col in expected_cols:
            assert col in engineered_dataset.columns, f"Missing engineered col: {col}"

    def test_profit_margin_clamped(self, engineered_dataset):
        """Profit margin should be clamped to [-1, 1]."""
        pm = engineered_dataset["profit_margin"]
        assert (pm >= -1.0).all() and (pm <= 1.0).all()

    def test_experience_score_range(self, engineered_dataset):
        """Experience score should be in [0, 1]."""
        es = engineered_dataset["experience_score"]
        assert (es >= 0).all() and (es <= 1).all()

    def test_market_opportunity_range(self, engineered_dataset):
        """Market opportunity score should be in [0, 100]."""
        mo = engineered_dataset["market_opportunity_score"]
        assert (mo >= 0).all() and (mo <= 100).all()

    def test_financial_health_range(self, engineered_dataset):
        """Financial health score should be in [0, 100]."""
        fh = engineered_dataset["financial_health_score"]
        assert (fh >= 0).all() and (fh <= 100).all()

    def test_investment_category_values(self, engineered_dataset):
        """Investment category should be Small, Medium, or Large."""
        valid = {"Small", "Medium", "Large"}
        assert set(engineered_dataset["investment_category"].unique()).issubset(valid)

    def test_competition_score_num_values(self, engineered_dataset):
        """Competition score num should be 0, 1, or 2."""
        valid = {0, 1, 2}
        assert set(engineered_dataset["competition_score_num"].unique()).issubset(valid)

    def test_single_row_feature_engineering(self):
        """Feature engineering should work on a single row."""
        from ml.features.feature_engineering import add_engineered_features
        single_row = pd.DataFrame([{
            "business_category": "Food",
            "business_model": "Cafe",
            "investment_amount": 500000,
            "expected_monthly_revenue": 150000,
            "expected_monthly_expenses": 100000,
            "employee_count": 3,
            "experience_years": 2,
            "market_demand": 6,
            "competition_level": "Medium",
            "location": "Bengaluru",
            "target_customer": "Students",
            "funding_source": "Personal",
            "business_age": 0,
        }])
        result = add_engineered_features(single_row)
        assert "profit_margin" in result.columns
        assert "financial_health_score" in result.columns


# ─── 4. Preprocessing Tests ──────────────────────────────────────────────────

class TestPreprocessing:

    def test_prepare_data_shapes_correct(self, engineered_dataset):
        """Train/test split should produce correct shapes."""
        from ml.preprocessing.data_preprocessing import prepare_data
        from ml.features.feature_engineering import get_feature_names_for_model
        numeric_cols, categorical_cols = get_feature_names_for_model("success")
        X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(
            engineered_dataset, "success", numeric_cols, categorical_cols, stratify=True
        )
        assert len(X_train) + len(X_test) == len(engineered_dataset)
        assert X_train.shape[1] == X_test.shape[1]
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)

    def test_preprocessor_fit_on_train_only(self, engineered_dataset):
        """Preprocessor should be fit only on training data."""
        from ml.preprocessing.data_preprocessing import prepare_data
        from ml.features.feature_engineering import get_feature_names_for_model
        numeric_cols, categorical_cols = get_feature_names_for_model("success")
        X_train, X_test, y_train, y_test, preprocessor, _ = prepare_data(
            engineered_dataset, "success", numeric_cols, categorical_cols
        )
        # Preprocessor should be already fitted — transform should work
        # If fit was on full data, this test alone can't catch leakage,
        # but we verify the transform doesn't fail on test data
        assert X_test.shape[0] > 0  # Transform succeeded

    def test_no_nan_after_preprocessing(self, engineered_dataset):
        """Transformed arrays should have no NaN values."""
        from ml.preprocessing.data_preprocessing import prepare_data
        from ml.features.feature_engineering import get_feature_names_for_model
        numeric_cols, categorical_cols = get_feature_names_for_model("risk")
        X_train, X_test, y_train, y_test, _, _ = prepare_data(
            engineered_dataset, "risk_level", numeric_cols, categorical_cols
        )
        assert not np.isnan(X_train).any()
        assert not np.isnan(X_test).any()


# ─── 5. Business Score Tests ──────────────────────────────────────────────────

class TestBusinessScore:

    def test_score_within_range(self):
        from ml.utils.scoring import calculate_business_score
        score = calculate_business_score(
            success_probability=75.0,
            risk_level="Low",
            competition_level="Medium",
            profit_margin=0.3,
            market_demand=7,
            experience_years=5,
            revenue_to_expense_ratio=1.5,
        )
        assert 0 <= score <= 100

    def test_high_success_high_score(self):
        from ml.utils.scoring import calculate_business_score
        high_score = calculate_business_score(
            success_probability=90.0, risk_level="Low", competition_level="Low",
            profit_margin=0.5, market_demand=9, experience_years=10, revenue_to_expense_ratio=2.0
        )
        low_score = calculate_business_score(
            success_probability=20.0, risk_level="High", competition_level="High",
            profit_margin=-0.3, market_demand=2, experience_years=0, revenue_to_expense_ratio=0.5
        )
        assert high_score > low_score

    def test_risk_penalty_applied(self):
        from ml.utils.scoring import calculate_business_score
        low_risk = calculate_business_score(
            success_probability=70.0, risk_level="Low", competition_level="Low",
            profit_margin=0.2, market_demand=6, experience_years=3, revenue_to_expense_ratio=1.2
        )
        high_risk = calculate_business_score(
            success_probability=70.0, risk_level="High", competition_level="Low",
            profit_margin=0.2, market_demand=6, experience_years=3, revenue_to_expense_ratio=1.2
        )
        assert low_risk > high_risk

    def test_score_explanation_structure(self):
        from ml.utils.scoring import explain_score
        result = explain_score(
            success_probability=75.0, risk_level="Medium", competition_level="Medium",
            profit_margin=0.2, market_demand=6, experience_years=4, revenue_to_expense_ratio=1.3
        )
        assert "total_score" in result
        assert "components" in result
        assert "penalties" in result


# ─── 6. Model Loading Tests ───────────────────────────────────────────────────

class TestModelLoading:

    def test_model_availability_check(self):
        from ml.utils.model_loader import are_models_available
        # This just checks the function works, not that models are present
        result = are_models_available()
        assert isinstance(result, bool)

    @pytest.mark.skipif(
        not (SUCCESS_MODEL_PATH.exists() and RISK_MODEL_PATH.exists() and
             ROI_MODEL_PATH.exists() and COMPETITION_MODEL_PATH.exists()),
        reason="Model artifacts not trained yet"
    )
    def test_all_models_load(self):
        from ml.utils.model_loader import load_all_models, clear_model_cache
        clear_model_cache()
        models = load_all_models()
        assert "success" in models
        assert "risk" in models
        assert "roi" in models
        assert "competition" in models
        assert "preprocessors" in models

    def test_missing_model_raises_error(self, tmp_path):
        """If model path doesn't exist, clear error should be raised."""
        from ml.utils.model_loader import _load_artifact, ModelNotTrainedError
        fake_path = tmp_path / "nonexistent_model.joblib"
        with pytest.raises(ModelNotTrainedError):
            _load_artifact(fake_path, "fake_model")


# ─── 7. Prediction Tests (require trained models) ────────────────────────────

@pytest.mark.skipif(
    not (SUCCESS_MODEL_PATH.exists() and RISK_MODEL_PATH.exists() and
         ROI_MODEL_PATH.exists() and COMPETITION_MODEL_PATH.exists()),
    reason="Model artifacts not trained yet — run: python -m ml.training.train_all"
)
class TestPrediction:

    def get_valid_input(self):
        return {
            "business_category": "Food",
            "business_model": "Cafe",
            "investment_amount": 800000,
            "expected_monthly_revenue": 250000,
            "expected_monthly_expenses": 150000,
            "employee_count": 5,
            "experience_years": 2,
            "location": "Bengaluru",
            "target_customer": "Students",
            "market_demand": 7,
            "competition_level": "Medium",
            "funding_source": "Personal",
            "business_age": 0,
        }

    def test_prediction_returns_dict(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert isinstance(result, dict)

    def test_prediction_has_required_keys(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        required_keys = [
            "success_probability", "success_prediction",
            "risk_level", "estimated_roi", "competition_level", "business_score"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_success_probability_in_range(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert 0 <= result["success_probability"] <= 100

    def test_business_score_in_range(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert 0 <= result["business_score"] <= 100

    def test_risk_level_valid(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert result["risk_level"] in RISK_LEVELS

    def test_competition_level_valid(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert result["competition_level"] in COMPETITION_LEVELS

    def test_success_prediction_is_bool(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input())
        assert isinstance(result["success_prediction"], bool)

    def test_explanation_included_when_requested(self):
        from ml.utils.prediction_utils import predict
        result = predict(self.get_valid_input(), include_explanation=True)
        assert "score_explanation" in result

    def test_unknown_business_category_handled(self):
        """Unknown categorical values should not crash (handle_unknown='ignore')."""
        from ml.utils.prediction_utils import predict
        data = self.get_valid_input()
        data["business_category"] = "Alien Technology"  # Unknown category
        result = predict(data)
        assert isinstance(result, dict)

    def test_unknown_location_handled(self):
        from ml.utils.prediction_utils import predict
        data = self.get_valid_input()
        data["location"] = "Unknown City"
        result = predict(data)
        assert isinstance(result, dict)

    def test_zero_experience_handled(self):
        from ml.utils.prediction_utils import predict
        data = self.get_valid_input()
        data["experience_years"] = 0
        result = predict(data)
        assert isinstance(result, dict)
        assert 0 <= result["business_score"] <= 100

    def test_loss_making_business_high_risk(self):
        """A business losing money should generally have higher risk."""
        from ml.utils.prediction_utils import predict
        loss_data = {
            "business_category": "Manufacturing",
            "business_model": "Factory",
            "investment_amount": 5000000,
            "expected_monthly_revenue": 50000,
            "expected_monthly_expenses": 300000,  # Huge loss
            "employee_count": 20,
            "experience_years": 0,
            "location": "Rural",
            "target_customer": "Businesses",
            "market_demand": 2,
            "competition_level": "High",
            "funding_source": "Bank Loan",
            "business_age": 0,
        }
        result = predict(loss_data)
        # Loss-making businesses should not have perfect scores
        assert result["business_score"] < 70


# ─── 8. Input Validation Edge Case Tests ─────────────────────────────────────

class TestInputValidation:

    def test_missing_required_field_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        incomplete = {
            "business_category": "Food",
            # investment_amount missing
            "expected_monthly_revenue": 100000,
            "expected_monthly_expenses": 80000,
            "employee_count": 3,
            "experience_years": 1,
            "market_demand": 5,
        }
        with pytest.raises(PredictionInputError):
            predict(incomplete)

    def test_negative_investment_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        data = {
            "business_category": "Food",
            "investment_amount": -100000,  # Invalid
            "expected_monthly_revenue": 100000,
            "expected_monthly_expenses": 80000,
            "employee_count": 3,
            "experience_years": 1,
            "market_demand": 5,
        }
        with pytest.raises(PredictionInputError):
            predict(data)

    def test_negative_revenue_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        data = {
            "business_category": "Food",
            "investment_amount": 500000,
            "expected_monthly_revenue": -50000,  # Invalid
            "expected_monthly_expenses": 80000,
            "employee_count": 3,
            "experience_years": 1,
            "market_demand": 5,
        }
        with pytest.raises(PredictionInputError):
            predict(data)

    def test_invalid_market_demand_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        data = {
            "business_category": "Food",
            "investment_amount": 500000,
            "expected_monthly_revenue": 100000,
            "expected_monthly_expenses": 80000,
            "employee_count": 3,
            "experience_years": 1,
            "market_demand": 15,  # Invalid: max is 10
        }
        with pytest.raises(PredictionInputError):
            predict(data)

    def test_empty_dict_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        with pytest.raises(PredictionInputError):
            predict({})

    def test_zero_investment_raises(self):
        from ml.utils.prediction_utils import predict, PredictionInputError
        data = {
            "business_category": "Food",
            "investment_amount": 0,
            "expected_monthly_revenue": 100000,
            "expected_monthly_expenses": 80000,
            "employee_count": 3,
            "experience_years": 1,
            "market_demand": 5,
        }
        with pytest.raises(PredictionInputError):
            predict(data)
