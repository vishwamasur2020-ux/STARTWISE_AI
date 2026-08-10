"""
STARTWISE AI — Stage 9 Marketing Recommendation Engine

Analyzes startup parameters + Stage 7 ML predictions to generate:
  1. Multi-factor scored and ranked marketing channels with dynamic explanations
  2. Recommended initial marketing budget allocation + 3 strategy scenarios (Low, Balanced, Aggressive)
  3. Tailored campaign concepts
  4. Content strategy across Social, Video, Blog, Email, WhatsApp
  5. Practical 30-Day Marketing Plan timeline
  6. Channel-specific relevant KPIs
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import math

from app.marketing.marketing_config import (
    MARKETING_WEIGHT_CONFIG,
    get_marketing_score_label,
    RECOMMENDED_MARKETING_BUDGET_RATIO,
    MIN_MARKETING_BUDGET,
    MAX_MARKETING_BUDGET,
    MARKETING_DISCLAIMER_TEXT,
)
from app.marketing.marketing_channels_dataset import MARKETING_CHANNELS_DATASET, MarketingChannelData


# ─── Marketing Profile ───────────────────────────────────────────────────────
class MarketingProfile:
    """Consolidated profile containing startup parameters and Stage 7 ML outputs."""

    def __init__(
        self,
        category: str,
        business_model: str,
        location: str,
        target_customer: str,
        budget: float,
        monthly_revenue: float = 0.0,
        monthly_expenses: float = 0.0,
        experience_years: int = 0,
        market_demand: str = "High",
        competition: str = "High",
        predicted_success_probability: float = 75.0,
        predicted_risk: str = "Low",
        predicted_roi: float = 25.0,
        business_score: float = 75.0,
    ):
        self.category = category
        self.business_model = business_model or "B2C"
        self.location = location or "India"
        self.target_customer = target_customer or "General Public"
        self.budget = budget
        self.monthly_revenue = monthly_revenue
        self.monthly_expenses = monthly_expenses
        self.experience_years = experience_years
        self.market_demand = market_demand
        self.competition = competition
        self.predicted_success_probability = predicted_success_probability
        self.predicted_risk = predicted_risk
        self.predicted_roi = predicted_roi
        self.business_score = business_score


# ─── Scored Channel Result ───────────────────────────────────────────────────
class ScoredChannelResult:
    """Individual scored marketing channel with dynamic explanation and budget."""

    def __init__(
        self,
        channel: MarketingChannelData,
        score: float,
        score_label: str,
        ranking_position: int,
        allocated_budget: float,
        explanation: List[str],
        sub_scores: Dict[str, float],
    ):
        self.channel = channel
        self.score = round(score, 1)
        self.score_label = score_label
        self.ranking_position = ranking_position
        self.allocated_budget = round(allocated_budget, 2)
        self.explanation = explanation
        self.sub_scores = sub_scores

    def to_dict(self) -> Dict[str, Any]:
        d = self.channel.to_dict()
        d["marketing_score"] = self.score
        d["score_label"] = self.score_label
        d["ranking_position"] = self.ranking_position
        d["allocated_budget"] = self.allocated_budget
        d["explanation"] = self.explanation
        d["sub_scores"] = self.sub_scores
        return d


# ─── Extensible Interface for Content Generation ────────────────────────────
class MarketingContentGenerator(ABC):
    """Interface allowing initial rule-based engine to be extended by future LLMs."""

    @abstractmethod
    def generate_campaign_ideas(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def generate_content_strategy(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_thirty_day_plan(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> List[Dict[str, Any]]:
        pass


# ─── Rule-Based Marketing Strategy Engine ───────────────────────────────────
class RuleBasedMarketingGenerator(MarketingContentGenerator):
    """Deterministic, dataset-driven marketing generator."""

    def generate_campaign_ideas(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> List[Dict[str, Any]]:
        cat = profile.category.lower()
        tc = profile.target_customer.lower()
        comp = profile.competition.lower()

        campaigns = []

        # Campaign 1: Launch Special
        if "food" in cat or "cafe" in cat:
            campaigns.append({
                "campaign_name": "Student & Youth Combo Festival",
                "platform": "Instagram & Campus",
                "objective": "Drive immediate foot traffic & social check-ins",
                "target_audience": profile.target_customer,
                "estimated_budget": 5000.0,
                "call_to_action": "Show Student ID for 20% Off",
                "description": "Launch 1+1 combo offers during peak afternoon hours promoted via Instagram Reels and Campus Ambassadors.",
            })
        elif "retail" in cat or "beauty" in cat:
            campaigns.append({
                "campaign_name": "Grand Opening Discount Blast",
                "platform": "Instagram & WhatsApp",
                "objective": "First 100 customer walk-ins & lead capture",
                "target_audience": profile.target_customer,
                "estimated_budget": 6000.0,
                "call_to_action": "Claim Exclusive Launch Coupon",
                "description": "Limited-time opening vouchers distributed via localized Instagram ads and WhatsApp direct messaging.",
            })
        else:
            campaigns.append({
                "campaign_name": "Free Consultation & Demo Week",
                "platform": "Google Ads & LinkedIn",
                "objective": "High-intent lead generation & appointments",
                "target_audience": profile.target_customer,
                "estimated_budget": 8000.0,
                "call_to_action": "Book Your Free Slot Today",
                "description": "High-converting search ad campaign leading to a dedicated landing page offering zero-cost initial consults.",
            })

        # Campaign 2: Competition / Differentiation
        if "high" in comp:
            campaigns.append({
                "campaign_name": "Local Influencer Review Surge",
                "platform": "Influencer & Instagram",
                "objective": "Build trust & differentiate from local competitors",
                "target_audience": "Local Foodies & Shoppers",
                "estimated_budget": 8000.0,
                "call_to_action": "Try Our Signature Special",
                "description": "Invite 5 regional micro-influencers to experience your service and post authentic video reviews.",
            })
        else:
            campaigns.append({
                "campaign_name": "First-Mover Referral Blitz",
                "platform": "WhatsApp & Referral",
                "objective": "Viral word-of-mouth customer acquisition",
                "target_audience": "Existing Customers",
                "estimated_budget": 4000.0,
                "call_to_action": "Refer a Friend, Get ₹200 Cashback",
                "description": "Give existing satisfied clients a unique referral code to share with friends and family.",
            })

        # Campaign 3: Local Authority / SEO
        campaigns.append({
            "campaign_name": "Google Maps 5-Star Review Sprint",
            "platform": "Google Business Profile",
            "objective": "Dominate local search rankings in your city",
            "target_audience": profile.location + " Residents",
            "estimated_budget": 2000.0,
            "call_to_action": "Leave a Review for a Free Beverage/Discount",
            "description": "Place QR codes at checkout encouraging customers to leave 5-star Google reviews for instant rewards.",
        })

        return campaigns

    def generate_content_strategy(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> Dict[str, Any]:
        cat = profile.category.title()

        return {
            "content_pillars": [
                "1. Signature Products & Behind-the-Scenes",
                "2. Customer Testimonials & 5-Star Reviews",
                "3. Promotional Deals & Seasonal Offers",
                "4. Educational Tips & Industry Insights",
                "5. Community & Founder Story",
            ],
            "social_media_posts": [
                f"Behind-the-scenes video showing how your {cat} items are crafted.",
                "Customer spotlight: Real customer testimonial showcasing their positive experience.",
                "Weekend Flash Sale Announcement with clear discount CTA.",
                "Interactive poll asking audience their favorite product feature.",
            ],
            "reels_and_shorts": [
                "15-second viral trend video highlighting your unique USP.",
                "Day in the life of a founder opening the store in " + profile.location + ".",
                "Before & After transformation / satisfying preparation clip.",
            ],
            "blog_ideas": [
                f"Top 5 Things to Look for When Choosing a {cat} Service in {profile.location}.",
                f"How {cat} Innovations Are Changing Customer Experience in 2026.",
            ],
            "email_templates": [
                "Welcome Email: 'Welcome to our family! Here is your 15% discount code.'",
                "Re-engagement Email: 'We miss you! Special offer inside for your next visit.'",
            ],
            "whatsapp_messages": [
                f"Hi 👋 Exclusive alert for our {profile.location} VIPs! Enjoy 20% off this weekend. Click to claim: [Link]",
            ],
            "call_to_actions": [
                "Book Free Appointment Now",
                "Claim Launch Voucher (Limited Stock)",
                "Visit Us Today in " + profile.location,
            ],
        }

    def generate_thirty_day_plan(self, profile: MarketingProfile, top_channels: List[ScoredChannelResult]) -> List[Dict[str, Any]]:
        c1_name = top_channels[0].channel.channel_name if top_channels else "Instagram"
        c2_name = top_channels[1].channel.channel_name if len(top_channels) > 1 else "Google Business"

        return [
            {
                "week": 1,
                "phase": "Brand Setup & Digital Foundation",
                "tasks": [
                    {
                        "task_name": "Setup Google Business Profile & Verify Location",
                        "channel": "Google Business Profile",
                        "expected_objective": "Map visibility & local search readiness",
                        "kpis": "Profile verified, 10 photos uploaded",
                    },
                    {
                        "task_name": "Create Professional Social Profiles (Instagram & Facebook)",
                        "channel": c1_name,
                        "expected_objective": "Consistent brand bio, highlights, and contact link",
                        "kpis": "Bio setup, grid aesthetic established",
                    },
                    {
                        "task_name": "Define Launch Campaign & Prepare Promotional Graphics",
                        "channel": "Content Marketing",
                        "expected_objective": "Prepare 10 launch posts & 3 reels in advance",
                        "kpis": "Content calendar populated",
                    },
                ],
            },
            {
                "week": 2,
                "phase": "Content Launch & Organic Reach",
                "tasks": [
                    {
                        "task_name": f"Publish 5 High-Quality Posts & 2 Reels on {c1_name}",
                        "channel": c1_name,
                        "expected_objective": "Build organic audience engagement & brand awareness",
                        "kpis": "Reach > 2,000, 150 Likes",
                    },
                    {
                        "task_name": "Launch WhatsApp Customer Broadcast Channel",
                        "channel": "WhatsApp Business",
                        "expected_objective": "Direct engagement with initial leads",
                        "kpis": "50 WhatsApp opt-ins",
                    },
                    {
                        "task_name": "Initiate Local Micro-Influencer Outreach (Send Invitations)",
                        "channel": "Influencer Marketing",
                        "expected_objective": "Confirm 3-5 influencer store visits",
                        "kpis": "5 confirmed influencer collaborations",
                    },
                ],
            },
            {
                "week": 3,
                "phase": "Paid Acquisition & Local Push",
                "tasks": [
                    {
                        "task_name": f"Launch Paid Ad Campaign on {c1_name}",
                        "channel": c1_name,
                        "expected_objective": "Targeted local traffic & lead capture",
                        "kpis": "CTR > 2.5%, 30 Lead conversions",
                    },
                    {
                        "task_name": "Execute Google Reviews QR Campaign at Checkout",
                        "channel": "Google Business Profile",
                        "expected_objective": "Boost local map ranking with 5-star reviews",
                        "kpis": "25 new 5-star Google reviews",
                    },
                    {
                        "task_name": "Distribute Campus & Local Neighborhood Flyers",
                        "channel": "Campus / Local Events",
                        "expected_objective": "Local foot traffic spike",
                        "kpis": "50 flyer coupons redeemed",
                    },
                ],
            },
            {
                "week": 4,
                "phase": "Analyze, Optimize & Scale",
                "tasks": [
                    {
                        "task_name": "Analyze Channel Conversion Rates & Customer Acquisition Cost",
                        "channel": "Analytics",
                        "expected_objective": "Identify top performing marketing channel",
                        "kpis": "CAC calculated, ROAS measured",
                    },
                    {
                        "task_name": "Re-allocate 70% of Remaining Budget to Best Performing Channel",
                        "channel": c1_name,
                        "expected_objective": "Maximize return on ad spend",
                        "kpis": "Conversion rate increased by 20%",
                    },
                    {
                        "task_name": "Launch Customer Referral & Loyalty Program",
                        "channel": "Referral Marketing",
                        "expected_objective": "Turn week 1-3 customers into brand advocates",
                        "kpis": "15 referral conversions",
                    },
                ],
            },
        ]


# ─── Core Marketing Engine Implementation ───────────────────────────────────
class MarketingRecommendationEngine:
    """Production-grade AI Marketing Recommendation Engine."""

    def __init__(self, channels_dataset: Optional[List[MarketingChannelData]] = None):
        self.channels = channels_dataset or MARKETING_CHANNELS_DATASET
        self.content_generator: MarketingContentGenerator = RuleBasedMarketingGenerator()

    def analyze_and_recommend(self, profile: MarketingProfile, top_k: int = 5) -> Dict[str, Any]:
        """Main entry point: scores channels, allocates budget, generates strategy."""

        # 1. Score each channel against profile
        scored_results: List[ScoredChannelResult] = []

        for channel in self.channels:
            score, sub_scores, explanation = self._calculate_channel_score(channel, profile)
            score_label = get_marketing_score_label(score)

            res = ScoredChannelResult(
                channel=channel,
                score=score,
                score_label=score_label,
                ranking_position=0,
                allocated_budget=0.0,
                explanation=explanation,
                sub_scores=sub_scores,
            )
            scored_results.append(res)

        # 2. Sort by score descending
        scored_results.sort(key=lambda r: r.score, reverse=True)

        # Assign ranking position
        for idx, res in enumerate(scored_results):
            res.ranking_position = idx + 1

        top_channels = scored_results[:top_k]

        # 3. Calculate Recommended Initial Marketing Budget
        raw_budget = profile.budget * RECOMMENDED_MARKETING_BUDGET_RATIO
        total_recommended_budget = max(MIN_MARKETING_BUDGET, min(MAX_MARKETING_BUDGET, raw_budget))

        # 4. Allocate Budget across Top Channels proportionally based on score
        total_top_score = sum(r.score for r in top_channels) or 1.0
        for r in top_channels:
            share = r.score / total_top_score
            r.allocated_budget = round(total_recommended_budget * share, 2)

        # 5. Generate Budget Scenarios
        budget_scenarios = self._generate_budget_scenarios(total_recommended_budget, top_channels)

        # 6. Calculate overall Strategy Marketing Score
        avg_top_score = sum(r.score for r in top_channels) / len(top_channels) if top_channels else 75.0
        overall_marketing_score = round(min(98.0, max(50.0, avg_top_score)), 1)

        # 7. Generate Campaign Ideas, Content Strategy, 30-Day Plan, KPIs
        campaign_ideas = self.content_generator.generate_campaign_ideas(profile, top_channels)
        content_strategy = self.content_generator.generate_content_strategy(profile, top_channels)
        thirty_day_plan = self.content_generator.generate_thirty_day_plan(profile, top_channels)
        kpis = self._select_relevant_kpis(top_channels)

        return {
            "profile": {
                "category": profile.category,
                "business_model": profile.business_model,
                "location": profile.location,
                "target_customer": profile.target_customer,
                "budget": profile.budget,
                "monthly_revenue": profile.monthly_revenue,
                "competition": profile.competition,
                "predicted_risk": profile.predicted_risk,
                "predicted_roi": profile.predicted_roi,
                "business_score": profile.business_score,
            },
            "strategy_name": f"AI Marketing Strategy for {profile.category}",
            "marketing_score": overall_marketing_score,
            "strategy_label": get_marketing_score_label(overall_marketing_score),
            "total_recommended_budget": total_recommended_budget,
            "strategy_type": "BALANCED",
            "recommended_channels": [r.to_dict() for r in top_channels],
            "budget_allocation": budget_scenarios,
            "campaign_ideas": campaign_ideas,
            "content_strategy": content_strategy,
            "thirty_day_plan": thirty_day_plan,
            "kpis": kpis,
            "disclaimer": MARKETING_DISCLAIMER_TEXT,
        }

    # ─── Private Channel Scoring Math ───────────────────────────────────────
    def _calculate_channel_score(
        self, channel: MarketingChannelData, profile: MarketingProfile
    ) -> (float, Dict[str, float], List[str]):
        reasons: List[str] = []
        sub: Dict[str, float] = {}

        # 1. Category Fit (20%)
        cat_lower = profile.category.lower()
        match_cat = any(c.lower() in cat_lower or cat_lower in c.lower() for c in channel.business_categories)
        if match_cat:
            sub["category_fit"] = 100.0
            reasons.append(f"Highly relevant for your '{profile.category}' industry.")
        else:
            sub["category_fit"] = 60.0

        # 2. Target Audience Fit (20%)
        tc_lower = profile.target_customer.lower()
        match_aud = any(a.lower() in tc_lower or tc_lower in a.lower() for a in channel.target_audience)
        if match_aud:
            sub["target_audience_fit"] = 100.0
            reasons.append(f"Directly reaches your target customer segment: '{profile.target_customer}'.")
        else:
            sub["target_audience_fit"] = 70.0

        # 3. Budget Fit (15%)
        raw_mkt_budget = profile.budget * RECOMMENDED_MARKETING_BUDGET_RATIO
        if raw_mkt_budget >= channel.minimum_budget:
            sub["budget_fit"] = 100.0
            reasons.append(f"Fits within your estimated marketing budget allocation.")
        else:
            sub["budget_fit"] = max(20.0, 100.0 - ((channel.minimum_budget - raw_mkt_budget) / 1000.0) * 10)

        # 4. Business Model Fit (15%)
        bm = (profile.business_model or "B2C").upper()
        if "B2B" in bm:
            sub["business_model_fit"] = channel.b2b_score * 10.0
        else:
            sub["business_model_fit"] = channel.b2c_score * 10.0

        # 5. Location Fit (10%)
        if channel.reach_level == "Local":
            sub["location_fit"] = channel.local_business_score * 10.0
            reasons.append(f"Optimized for local visibility in {profile.location}.")
        else:
            sub["location_fit"] = channel.digital_score * 10.0

        # 6. Competition Fit (10%) - Stage 7 Signal
        comp = (profile.competition or "High").lower()
        if "high" in comp:
            # If competition is high, boost local SEO, reviews, and influencer trust channels
            if channel.channel_name in ["Google Business Profile", "Influencer Marketing", "Instagram Marketing", "Referral & Loyalty Program"]:
                sub["competition_fit"] = 100.0
                reasons.append(f"High competition adaptation: Builds strong brand trust & local map dominance.")
            else:
                sub["competition_fit"] = 70.0
        else:
            sub["competition_fit"] = 85.0

        # 7. Risk Fit (5%) - Stage 7 Signal
        risk = (profile.predicted_risk or "Low").lower()
        if "high" in risk:
            # High risk -> favor low cost / easy channels
            if channel.cost_level == "Low" or channel.minimum_budget <= 3000.0:
                sub["demand_fit"] = 100.0
                reasons.append(f"Risk adaptation: Low financial commitment for pilot testing.")
            else:
                sub["demand_fit"] = 50.0
        else:
            sub["demand_fit"] = 90.0

        # 8. Time to Results Fit (5%)
        if "Immediate" in channel.time_to_results or "Fast" in channel.time_to_results:
            sub["time_to_results_fit"] = 100.0
        else:
            sub["time_to_results_fit"] = 70.0

        # Calculate final weighted score
        final_score = sum(sub[k] * MARKETING_WEIGHT_CONFIG[k] for k in MARKETING_WEIGHT_CONFIG)

        return round(final_score, 1), sub, reasons

    # ─── Budget Scenarios Generator ──────────────────────────────────────────
    def _generate_budget_scenarios(self, total_budget: float, top_channels: List[ScoredChannelResult]) -> Dict[str, Any]:
        balanced_alloc = {r.channel.channel_name: r.allocated_budget for r in top_channels}

        # Low Budget Scenario (50% of budget, zero in high cost channels)
        low_budget_total = round(total_budget * 0.5, 2)
        low_alloc = {}
        organic_channels = [r for r in top_channels if r.channel.cost_level == "Low"] or top_channels[:3]
        per_ch_low = round(low_budget_total / len(organic_channels), 2)
        for r in organic_channels:
            low_alloc[r.channel.channel_name] = per_ch_low

        # Aggressive Scenario (180% of budget, scaling paid ads & influencers)
        agg_budget_total = round(total_budget * 1.8, 2)
        agg_alloc = {}
        for r in top_channels:
            multiplier = 2.0 if r.channel.cost_level in ["Medium", "High"] else 1.2
            agg_alloc[r.channel.channel_name] = round(r.allocated_budget * multiplier, 2)

        return {
            "recommended_total": total_budget,
            "scenarios": {
                "LOW_BUDGET": {
                    "label": "Low Budget Strategy",
                    "total": low_budget_total,
                    "description": "Focus on organic Instagram, Google Business Profile, WhatsApp direct outreach, and referral word-of-mouth.",
                    "allocation": low_alloc,
                },
                "BALANCED": {
                    "label": "Balanced Strategy",
                    "total": total_budget,
                    "description": "Optimized mix of local organic search, targeted social media ads, and micro-influencer reviews.",
                    "allocation": balanced_alloc,
                },
                "AGGRESSIVE": {
                    "label": "Aggressive Growth Strategy",
                    "total": agg_budget_total,
                    "description": "Scale paid Google search ads, multi-creator influencer campaigns, and retargeting ads for maximum market capture.",
                    "allocation": agg_alloc,
                },
            },
        }

    # ─── KPI Selector ────────────────────────────────────────────────────────
    def _select_relevant_kpis(self, top_channels: List[ScoredChannelResult]) -> List[Dict[str, str]]:
        kpis = [
            {"metric": "Estimated Monthly Reach", "target": "15,000 - 30,000 Impressions", "category": "Awareness"},
            {"metric": "Target Click-Through Rate (CTR)", "target": "2.5% - 4.0%", "category": "Engagement"},
            {"metric": "Monthly Customer Leads", "target": "40 - 80 Qualified Leads", "category": "Conversions"},
            {"metric": "Customer Acquisition Cost (CAC)", "target": "₹150 - ₹350 per customer", "category": "Efficiency"},
            {"metric": "Return on Ad Spend (ROAS)", "target": "3.5x - 5.0x ROAS", "category": "ROI"},
            {"metric": "Google Maps Profile Views", "target": "1,200+ monthly views", "category": "Local SEO"},
        ]
        return kpis
