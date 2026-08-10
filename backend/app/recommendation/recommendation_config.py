"""
STARTWISE AI — Franchise Recommendation Engine Configuration (Stage 8)

Configurable feature weights, thresholds, and qualitative label mappings
for the hybrid AI recommendation system.
"""

from typing import Dict, Any

# ─── Configurable Weights for Hybrid Recommendation Score ─────────────────────
# Total sum = 1.0 (100%)
WEIGHT_CONFIG: Dict[str, float] = {
    "budget_fit": 0.25,        # 25% — Investment budget ceiling & ratio fit
    "industry_fit": 0.20,      # 20% — Category/Industry alignment
    "location_fit": 0.15,      # 15% — Target city/geography availability
    "roi_fit": 0.15,           # 15% — Expected ROI compatibility
    "risk_fit": 0.10,          # 10% — Risk preference vs franchise risk
    "experience_fit": 0.10,    # 10% — Required experience compatibility
    "demand_fit": 0.05,        # 5%  — Market demand score alignment
}

# ─── Hard Filter Parameters ──────────────────────────────────────────────────
# Allow franchises whose minimum investment is up to BUDGET_FLEXIBILITY_RATIO times user budget
BUDGET_FLEXIBILITY_RATIO: float = 1.25  # Max budget + 25% flexibility for strict filter

# ─── Qualitative Match Labels ────────────────────────────────────────────────
def get_match_label(score: float) -> str:
    """Map match score percentage (0-100) to qualitative recommendation rating."""
    if score >= 90.0:
        return "Excellent Match"
    elif score >= 75.0:
        return "Strong Match"
    elif score >= 60.0:
        return "Good Match"
    elif score >= 40.0:
        return "Moderate Match"
    else:
        return "Weak Match"


# Synthetic Data Disclaimer text
RECOMMENDATION_DISCLAIMER = (
    "DEMO / SYNTHETIC DATA: Financial parameters (investment ranges, estimated ROI) "
    "are indicative estimates for academic demonstration and do not constitute guaranteed returns."
)
