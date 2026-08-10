"""
STARTWISE AI — Stage 9 Marketing Engine Configuration

Configurable weights, threshold flexibility ratios, qualitative score labels,
budget scenario allocations, and data disclaimers.
Allows tuning channel scoring without modifying core recommendation algorithms.
"""

from typing import Dict

# ─── Multi-Factor Channel Scoring Weights (Total = 1.00) ────────────────────
MARKETING_WEIGHT_CONFIG: Dict[str, float] = {
    "category_fit": 0.20,       # Industry & category relevance
    "target_audience_fit": 0.20, # Target customer demographic alignment
    "budget_fit": 0.15,          # Financial budget availability vs channel minimum
    "business_model_fit": 0.15,  # B2C vs B2B suitability
    "location_fit": 0.10,        # Local vs nationwide reach match
    "competition_fit": 0.10,     # Adaptation to high/low competitive density
    "demand_fit": 0.05,          # Consumer market demand signal
    "time_to_results_fit": 0.05, # Speed to lead generation
}

# ─── Marketing Strategy Score Qualitative Labels ─────────────────────────────
MARKETING_SCORE_LABELS = {
    (90, 100): "Excellent Strategy",
    (75, 89): "Strong Strategy",
    (60, 74): "Good Strategy",
    (40, 59): "Moderate Strategy",
    (0, 39): "Weak Strategy",
}

def get_marketing_score_label(score: float) -> str:
    for (low, high), label in MARKETING_SCORE_LABELS.items():
        if low <= score <= high:
            return label
    return "Good Strategy"

# ─── Initial Marketing Allocation Percentage ───────────────────────────────
# Recommends 5% - 10% of total initial capital investment for launching marketing campaigns
RECOMMENDED_MARKETING_BUDGET_RATIO = 0.08  # 8% of total startup investment

# Minimum and Maximum marketing budget caps (INR)
MIN_MARKETING_BUDGET = 10000.0   # INR 10,000
MAX_MARKETING_BUDGET = 500000.0  # INR 500,000

# ─── Data Disclaimer ────────────────────────────────────────────────────────
MARKETING_DISCLAIMER_TEXT = (
    "INDICATIVE ESTIMATES: Marketing channel budget allocations, reach figures, and expected "
    "conversion metrics are dataset-driven indicative estimates. Advertising costs vary based "
    "on live auction bidding and audience targeting. Customer acquisition rates are not guaranteed."
)
