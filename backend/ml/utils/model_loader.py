"""
STARTWISE AI — Model Loader (Stage 6)

Loads trained ML model artifacts from disk using joblib.
Uses module-level caching to avoid reloading on every prediction.

IMPORTANT:
    Models must be trained first using:
        python -m ml.training.train_all

    If artifacts are missing, a clear error is raised.

Usage:
    from ml.utils.model_loader import load_all_models
    models = load_all_models()
    success_model = models["success"]
    preprocessors = models["preprocessors"]
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import joblib

from ml.ml_config import (
    SUCCESS_MODEL_PATH, SUCCESS_PREPROCESSOR_PATH,
    RISK_MODEL_PATH, RISK_PREPROCESSOR_PATH,
    ROI_MODEL_PATH, ROI_PREPROCESSOR_PATH,
    COMPETITION_MODEL_PATH, COMPETITION_PREPROCESSOR_PATH,
)


class ModelNotTrainedError(Exception):
    """Raised when a model artifact is not found on disk."""
    pass


def _load_artifact(path: Path, label: str):
    """Load a single joblib artifact with clear error handling."""
    if not path.exists():
        raise ModelNotTrainedError(
            f"Model artifact not found: {path}\n"
            f"Please train all models first by running:\n"
            f"  python -m ml.training.train_all"
        )
    try:
        artifact = joblib.load(path)
        return artifact
    except Exception as e:
        raise ModelNotTrainedError(
            f"Failed to load {label} from {path}: {e}"
        ) from e


@lru_cache(maxsize=1)
def load_all_models() -> Dict[str, Any]:
    """
    Load all trained ML models and preprocessors.
    Results are cached in memory after first load.

    Returns:
        dict with keys:
            - "success":          RandomForestClassifier
            - "risk":             DecisionTreeClassifier
            - "roi":              LinearRegression
            - "competition":      RandomForestClassifier
            - "preprocessors": {
                "success":        fitted ColumnTransformer
                "risk":           fitted ColumnTransformer
                "roi":            fitted ColumnTransformer
                "competition":    fitted ColumnTransformer
              }

    Raises:
        ModelNotTrainedError: If any artifact file is missing
    """
    models = {
        "success":    _load_artifact(SUCCESS_MODEL_PATH, "Success Model"),
        "risk":       _load_artifact(RISK_MODEL_PATH, "Risk Model"),
        "roi":        _load_artifact(ROI_MODEL_PATH, "ROI Model"),
        "competition": _load_artifact(COMPETITION_MODEL_PATH, "Competition Model"),
        "preprocessors": {
            "success":    _load_artifact(SUCCESS_PREPROCESSOR_PATH, "Success Preprocessor"),
            "risk":       _load_artifact(RISK_PREPROCESSOR_PATH, "Risk Preprocessor"),
            "roi":        _load_artifact(ROI_PREPROCESSOR_PATH, "ROI Preprocessor"),
            "competition": _load_artifact(COMPETITION_PREPROCESSOR_PATH, "Competition Preprocessor"),
        },
    }
    return models


def are_models_available() -> bool:
    """Check if all model artifacts are present without loading them."""
    paths = [
        SUCCESS_MODEL_PATH, SUCCESS_PREPROCESSOR_PATH,
        RISK_MODEL_PATH, RISK_PREPROCESSOR_PATH,
        ROI_MODEL_PATH, ROI_PREPROCESSOR_PATH,
        COMPETITION_MODEL_PATH, COMPETITION_PREPROCESSOR_PATH,
    ]
    return all(p.exists() for p in paths)


def clear_model_cache() -> None:
    """Clear the loaded model cache (useful for testing or model updates)."""
    load_all_models.cache_clear()


if __name__ == "__main__":
    if are_models_available():
        print("All model artifacts found.")
        models = load_all_models()
        print(f"Loaded: {list(models.keys())}")
    else:
        print("Model artifacts missing. Run: python -m ml.training.train_all")
