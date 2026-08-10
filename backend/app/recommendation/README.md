# STARTWISE AI — Stage 8 Franchise Recommendation Engine Architecture

## Overview

The **Franchise Recommendation Engine** is the second major machine learning and decision-intelligence module of STARTWISE AI. It provides personalized, multi-factor franchise recommendations based on a founder's startup profile, budget constraints, risk tolerance, and Stage 7 ML feasibility outputs.

---

## 1. Recommendation Problem Formulation

Finding the optimal franchise is a **multi-criteria decision-making (MCDM)** problem constrained by strict financial ceilings and geographical availability. Pure collaborative filtering (e.g. user-item ratings) cannot be used because early-stage startup founders do not have prior rating histories.

Therefore, STARTWISE AI employs a **Hybrid Content-Based & Nearest-Neighbors (KNN) Recommendation System**:
1. **Hard Constraints Filtering**: Eliminates non-viable candidates (e.g., investment exceeding budget flexibility ceiling).
2. **Vector Space Embedding & Cosine Similarity**: Maps user requirements and franchise feature vectors into a multi-dimensional normalized space using Scikit-Learn `NearestNeighbors`.
3. **Domain Compatibility Scoring**: Evaluates domain-specific metrics (Budget Fit, Industry Alignment, Location Availability, ROI Match, Risk Compatibility, Experience Level, Market Demand).
4. **Stage 7 ML Feedback Integration**: Dynamically adjusts recommendations using predicted risk and ROI signals.

---

## 2. Feature Engineering & Vectorization

### Numerical Features (`StandardScaler`)
- `minimum_investment` (INR)
- `maximum_investment` (INR)
- `roi` (Annual estimated ROI %)
- `experience_required` (Years)
- `market_demand` (1–10 scale)

### Categorical Features (`OneHotEncoder`)
- `industry` (Food, Retail, Healthcare, Education, Technology, Services, etc.)
- `risk_level` (Low, Medium, High)

---

## 3. Hybrid Match Scoring Methodology

The final `match_score` (0–100%) is calculated using a hybrid weighted blend:

$$\text{Match Score} = 0.35 \times \text{KNN Cosine Similarity} + 0.65 \times \text{Domain Compatibility Score}$$

Where the **Domain Compatibility Score** is configured in `recommendation_config.py`:
- **Budget Fit (25%)**: Penalizes franchises requiring capital above the user's budget limit.
- **Industry Alignment (20%)**: Full score for exact category match; partial for adjacent categories.
- **Location Availability (15%)**: City-level match (100%), State-level match (85%), Nationwide (70%).
- **ROI Compatibility (15%)**: Evaluates franchise ROI against target expected return.
- **Risk Profile (10%)**: Aligns user risk preference with franchise risk rating.
- **Experience Requirement (10%)**: Verifies founder experience meets minimum criteria.
- **Market Demand (5%)**: Rewards high consumer demand scores.

---

## 4. Stage 7 ML Signals Integration

- **High Predicted Risk**: If Stage 7 ML predicts "High Risk" for the startup concept, the recommender automatically prioritizes **Low Risk** franchises with proven turnkey operational models.
- **Low Predicted ROI**: If Stage 7 ML predicts modest ROI, the engine prioritizes higher-ROI franchise candidates to improve net returns.

---

## 5. Alternative Match Relaxation Fallback

If fewer than 5 franchises satisfy strict budget/category filters:
1. Strict filtering is relaxed to expand the candidate pool (up to 200% of user budget).
2. Candidates from adjacent categories are evaluated.
3. Relaxed candidates are tagged as `"recommendation_type": "ALTERNATIVE"` in the database and UI, clearly indicating that filters were expanded.

---

## 6. Academic / Viva Q&A

### Q1: Why use NearestNeighbors instead of simple if/else rules?
> **Answer**: Hardcoded rules fail gracefully when exact matches are missing and cannot quantify multi-dimensional trade-offs (e.g. comparing a franchise with slightly higher investment but much higher ROI against one with low risk). `NearestNeighbors` computes continuous spatial similarity distances in feature space.

### Q2: Why use Cosine Distance instead of Euclidean Distance?
> **Answer**: Cosine distance measures vector orientation rather than magnitude, ensuring large differences in absolute rupees do not disproportionately dominate smaller normalized features like ROI or experience years.

### Q3: What is the synthetic data disclaimer?
> **Answer**: All franchise financial parameters in the seed dataset are marked as `DEMO / SYNTHETIC DATA` for academic demonstration purposes, ensuring users are not misled by guaranteed returns.
