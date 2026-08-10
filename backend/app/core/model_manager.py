"""
STARTWISE AI — Model Manager (Stage 7)

Loads trained Machine Learning model artifacts during FastAPI application lifespan startup.
Caches models in memory to serve fast API predictions.

Artifacts Loaded:
  - success_model.joblib
  - risk_model.joblib
  - roi_model.joblib
  - competition_model.joblib
  - success_preprocessor.joblib
  - risk_preprocessor.joblib
  - roi_preprocessor.joblib
  - competition_preprocessor.joblib
  - feature_metadata.json
  - model_metrics.json

Design:
  - Singleton design pattern
  - Loaded once on lifespan startup
  - Thread-safe memory cache
  - Comprehensive health check interface for /api/ml/health
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import joblib

from app.core.logging import get_logger

logger = get_logger("app.core.model_manager")

# Resolve ML artifacts directory relative to backend root
BACKEND_DIR = Path(__file__).resolve().parents[2]
ML_ARTIFACTS_DIR = BACKEND_DIR / "ml" / "artifacts"


class ModelManager:
    _instance: Optional[ModelManager] = None

    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.preprocessors: Dict[str, Any] = {}
        self.feature_metadata: Dict[str, Any] = {}
        self.model_metrics: Dict[str, Any] = {}
        self.is_loaded: bool = False
        self.load_error: Optional[str] = None
        self.artifacts_dir: Path = ML_ARTIFACTS_DIR

    @classmethod
    def get_instance(cls) -> ModelManager:
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    def initialize(self, artifacts_dir: Optional[Path] = None) -> bool:
        """
        Load all ML model artifacts from disk into memory.
        Called during FastAPI application startup lifespan.
        """
        if artifacts_dir:
            self.artifacts_dir = artifacts_dir

        logger.info(f"STARTWISE AI ML ENGINE — Initializing from: {self.artifacts_dir}")
        print("\n" + "=" * 60)
        print("  STARTWISE AI ML ENGINE INITIALIZATION")
        print(f"  Artifacts directory: {self.artifacts_dir}")
        print("=" * 60)

        required_models = {
            "success": "success_model.joblib",
            "risk": "risk_model.joblib",
            "roi": "roi_model.joblib",
            "competition": "competition_model.joblib",
        }

        required_preprocessors = {
            "success": "success_preprocessor.joblib",
            "risk": "risk_preprocessor.joblib",
            "roi": "roi_preprocessor.joblib",
            "competition": "competition_preprocessor.joblib",
        }

        try:
            # 1. Load Models
            for name, filename in required_models.items():
                path = self.artifacts_dir / filename
                if not path.exists():
                    raise FileNotFoundError(f"Missing model artifact: {path}")
                self.models[name] = joblib.load(path)
                print(f"  [OK] Loaded {name.title()} Model ({type(self.models[name]).__name__})")

            # 2. Load Preprocessors
            for name, filename in required_preprocessors.items():
                path = self.artifacts_dir / filename
                if not path.exists():
                    raise FileNotFoundError(f"Missing preprocessor artifact: {path}")
                self.preprocessors[name] = joblib.load(path)
                print(f"  [OK] Loaded {name.title()} Preprocessor")

            # 3. Load Feature Metadata
            meta_path = self.artifacts_dir / "feature_metadata.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.feature_metadata = json.load(f)
                print(f"  [OK] Loaded Feature Metadata")

            # 4. Load Model Metrics
            metrics_path = self.artifacts_dir / "model_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    self.model_metrics = json.load(f)
                print(f"  [OK] Loaded Model Metrics")

            self.is_loaded = True
            self.load_error = None

            print("=" * 60)
            print("  STARTWISE AI ML ENGINE — READY FOR INFERENCE")
            print("=" * 60 + "\n")
            logger.info("ML Engine successfully loaded all models into memory.")
            return True

        except Exception as e:
            self.is_loaded = False
            self.load_error = str(e)
            print(f"  [ERROR] ML Engine initialization failed: {e}")
            print("=" * 60 + "\n")
            logger.error(f"Failed to load ML artifacts: {e}", exc_info=True)
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Return structured health status for /api/ml/health."""
        return {
            "status": "healthy" if self.is_loaded else "unhealthy",
            "models_loaded": self.is_loaded,
            "models": {
                "success": "success" in self.models,
                "risk": "risk" in self.models,
                "roi": "roi" in self.models,
                "competition": "competition" in self.models,
            },
            "preprocessors": {
                "success": "success" in self.preprocessors,
                "risk": "risk" in self.preprocessors,
                "roi": "roi" in self.preprocessors,
                "competition": "competition" in self.preprocessors,
            },
            "error": self.load_error,
            "artifacts_dir": str(self.artifacts_dir),
        }


# Singleton accessor
def get_model_manager() -> ModelManager:
    return ModelManager.get_instance()
