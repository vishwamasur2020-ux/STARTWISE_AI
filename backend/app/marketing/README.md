# STARTWISE AI — Stage 9 AI Marketing & Promotion Strategy Engine Architecture

## Overview

The **AI Marketing & Promotion Strategy Engine** is the third major intelligence module of STARTWISE AI. It generates personalized, multi-factor marketing strategies by synthesizing startup profile parameters (category, model, target customer, location, budget, experience) with Stage 7 ML predictions (`success_probability`, `risk_level`, `estimated_roi`, `competition_level`, `business_score`).

---

## 1. Multi-Factor Channel Scoring Methodology

Rather than returning static channel lists, STARTWISE AI scores each of the 19 structured channels using a transparent weighted scoring system configured in `marketing_config.py`:

$$\text{Channel Score} = \sum_{i=1}^{8} w_i \cdot S_i$$

### Weight Configuration (`marketing_config.py`)
- **Category Fit (20%)**: Evaluates industry-specific channel effectiveness (e.g. Food -> Instagram/Google Business; Tech -> LinkedIn/SEO).
- **Target Audience Fit (20%)**: Aligns channel user demographic with startup target customer segment (Gen Z, Students, Families, B2B Executives).
- **Budget Fit (15%)**: Verifies calculated marketing allocation satisfies channel minimum financial threshold.
- **Business Model Fit (15%)**: Distinguishes B2C consumer reach vs B2B enterprise outreach.
- **Location Fit (10%)**: Rewards local map visibility for physical outlets and regional digital reach for online models.
- **Competition Adaptation (10%)**:
  - *High Competition*: Prioritizes local SEO, Google reviews, micro-influencers, and differentiation.
  - *Low Competition*: Focuses on first-mover brand awareness and referral viral loops.
- **Demand Signal (5%)**: Adjusts for market demand level.
- **Time to Results (5%)**: Favors immediate lead generation channels for early-stage cashflow.

---

## 2. Stage 7 ML Signals Integration

- **Risk-Aware Strategy**: If Stage 7 ML predicts **High Risk**, the engine automatically shifts priority toward low-cost organic channels (Google Business, WhatsApp, Instagram) and small pilot experiments, preventing high upfront ad loss.
- **ROI-Aware Strategy**: If Stage 7 ML predicts **High ROI**, the system recommends scaling paid search (Google Ads) and influencer partnerships to maximize customer acquisition velocity.
- **Competition-Aware Strategy**: If Stage 7 ML predicts **High Competition**, the engine emphasizes Google 5-star review sprints, local differentiation, and student/campus ambassador programs.

---

## 3. Budget Allocation & Scenario Engine

The engine calculates a realistic recommended initial marketing budget using the ratio:

$$\text{Recommended Marketing Allocation} = \text{Total Startup Investment} \times 0.08$$

Bounded between **₹10,000** and **₹500,000**. It then provides 3 distinct strategy scenarios:
1. **Low Budget Strategy**: 50% of budget focusing exclusively on zero/low-cost organic channels.
2. **Balanced Strategy**: 100% of budget distributed across Top 5 ranked channels.
3. **Aggressive Growth Strategy**: 180% budget scaling paid ads, influencer sponsorships, and retargeting campaigns.

---

## 4. Extensible LLM Architecture

The core generator follows an abstract base interface:

```python
class MarketingContentGenerator(ABC):
    @abstractmethod
    def generate_campaign_ideas(self, profile, top_channels) -> List[Dict]: pass

    @abstractmethod
    def generate_content_strategy(self, profile, top_channels) -> Dict: pass

    @abstractmethod
    def generate_thirty_day_plan(self, profile, top_channels) -> List[Dict]: pass
```

- **Current Implementation**: `RuleBasedMarketingGenerator` — Deterministic, fast, dataset-driven, and offline-compatible.
- **Future Implementation**: `LLMMarketingGenerator` — Pluggable OpenAI/Gemini wrapper for creative copy generation without breaking API contracts.

---

## 5. Academic / Viva Q&A

### Q1: Why not rely purely on LLM prompts for marketing advice?
> **Answer**: LLM prompts can produce non-deterministic, hallucinatory budget numbers and unverified channel costs. The rule-based engine enforces mathematical budget caps, deterministic channel ranking, and empirical risk/competition adaptations while remaining fast and offline-ready.

### Q2: How does the system prevent unachievable marketing promises?
> **Answer**: All reach, conversion rates, and budget allocations are explicitly labeled with the disclaimer: `"INDICATIVE ESTIMATES: Financial parameters and conversion rates are dataset-driven estimates for academic project demonstration."`

### Q3: How is the 30-Day plan structured?
> **Answer**: It follows a 4-phase progression:
> - **Week 1**: Brand Setup & Digital Foundation (Google Business, social handles).
> - **Week 2**: Content Launch & Organic Reach (Posts, Reels, WhatsApp opt-ins).
> - **Week 3**: Paid Acquisition & Local Push (Targeted ads, review sprint).
> - **Week 4**: Analyze, Optimize & Scale (CAC calculation, double down on top channel).
