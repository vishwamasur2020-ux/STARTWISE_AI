"""
STARTWISE AI — Database Seeding Script (Stage 3)
Populates production-ready franchise data for matching and prediction engines.
Seed Brands: Tea Time, DTDC, FirstCry, Lenskart, Naturals, Apollo Pharmacy, Amul, Domino's.
"""

import asyncio
from sqlalchemy import select
from app.database.session import AsyncSessionLocal, engine, Base
from app.models.models import Franchise, RiskLevel, BusinessCategory
from app.core.logging import get_logger

logger = get_logger(__name__)

SAMPLE_FRANCHISES = [
    {
        "franchise_name": "Tea Time",
        "industry": BusinessCategory.food.value,
        "minimum_investment": 400000.0,
        "maximum_investment": 600000.0,
        "roi": 45.0,
        "risk_level": RiskLevel.low.value,
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "website": "https://teatime.in",
        "contact_email": "franchise@teatime.in",
        "description": "India's largest tea chain with over 3,000+ outlets across India serving authentic tea, coffee, and quick bites.",
        "logo_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Low initial capital requirement",
            "High ROI & quick payback within 6-9 months",
            "Turnkey setup with staff training included",
        ],
        "disadvantages": [
            "High dependency on local footfall",
            "Intense competition in tea segment",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "DTDC Express",
        "industry": BusinessCategory.retail.value,
        "minimum_investment": 150000.0,
        "maximum_investment": 300000.0,
        "roi": 35.0,
        "risk_level": RiskLevel.low.value,
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "website": "https://www.dtdc.in",
        "contact_email": "channel@dtdc.com",
        "description": "Leading courier, parcel, and express delivery logistics provider operating nationwide with 12,000+ pin codes served.",
        "logo_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Established brand value & nationwide trust",
            "Minimal infrastructure & inventory risk",
            "Steady B2B and retail order flow",
        ],
        "disadvantages": [
            "Margins regulated by central corporate pricing",
            "Requires active daily operations management",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "FirstCry",
        "industry": BusinessCategory.retail.value,
        "minimum_investment": 2000000.0,
        "maximum_investment": 3500000.0,
        "roi": 28.0,
        "risk_level": RiskLevel.medium.value,
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "website": "https://www.firstcry.com",
        "contact_email": "retail@firstcry.com",
        "description": "Asia's largest online & offline store for baby and kids care products, clothing, toys, and parenting essentials.",
        "logo_url": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Monopoly positioning in kids retail space",
            "Omnichannel inventory & ERP integration",
            "High customer lifetime value (LTV)",
        ],
        "disadvantages": [
            "Higher working capital for inventory",
            "Requires prime retail commercial space (1000+ sq ft)",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "Lenskart",
        "industry": BusinessCategory.healthcare.value,
        "minimum_investment": 3000000.0,
        "maximum_investment": 4500000.0,
        "roi": 32.0,
        "risk_level": RiskLevel.medium.value,
        "city": "Gurugram",
        "state": "Haryana",
        "country": "India",
        "website": "https://www.lenskart.com",
        "contact_email": "franchise@lenskart.com",
        "description": "India's premier tech-enabled eyewear retailer providing prescription glasses, sunglasses, and 3D virtual try-ons.",
        "logo_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Zero inventory risk (FOFO model)",
            "Automated optical testing machines supplied",
            "Strong omni-channel marketing support",
        ],
        "disadvantages": [
            "Strict location selection standards",
            "High initial store setup cost",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "Naturals Beauty Salon",
        "industry": BusinessCategory.services.value if hasattr(BusinessCategory, "services") else "Services",
        "minimum_investment": 3500000.0,
        "maximum_investment": 5000000.0,
        "roi": 30.0,
        "risk_level": RiskLevel.medium.value,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "website": "https://naturals.in",
        "contact_email": "franchise@naturals.in",
        "description": "India's No.1 unisex hair and beauty salon chain with 700+ salons empowering women entrepreneurs across India.",
        "logo_url": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "High gross profit margins on beauty services",
            "Comprehensive beautician staff recruitment & training",
            "Strong brand recognition and celebrity endorsements",
        ],
        "disadvantages": [
            "Staff retention and service quality management",
            "Seasonal revenue fluctuations",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "Apollo Pharmacy",
        "industry": BusinessCategory.healthcare.value,
        "minimum_investment": 1000000.0,
        "maximum_investment": 1800000.0,
        "roi": 25.0,
        "risk_level": RiskLevel.low.value,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "website": "https://www.apollopharmacy.in",
        "contact_email": "franchise@apollopharmacy.org",
        "description": "Asia's largest pharmacy retail network operating 5,000+ outlets delivering genuine medicines 24/7.",
        "logo_url": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Recession-proof essential healthcare industry",
            "100% genuine medicine supply chain guarantee",
            "Apollo 24|7 digital integration",
        ],
        "disadvantages": [
            "Mandatory Registered Pharmacist license required",
            "Regulated profit margins on DPCO drugs",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "Amul Parlour",
        "industry": BusinessCategory.food.value,
        "minimum_investment": 200000.0,
        "maximum_investment": 500000.0,
        "roi": 40.0,
        "risk_level": RiskLevel.low.value,
        "city": "Anand",
        "state": "Gujarat",
        "country": "India",
        "website": "https://amul.com",
        "contact_email": "retail@amul.coop",
        "description": "The Taste of India — exclusive Amul ice cream, dairy, and beverage scoops parlours with zero royalty or profit sharing.",
        "logo_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "No royalty or profit sharing fees",
            "Massive brand pull & household trust",
            "Very affordable initial setup investment",
        ],
        "disadvantages": [
            "Cold chain & deep freezer power backup required",
            "Fixed trade commission rates",
        ],
        "is_active": True,
    },
    {
        "franchise_name": "Domino's Pizza",
        "industry": BusinessCategory.food.value,
        "minimum_investment": 5000000.0,
        "maximum_investment": 10000000.0,
        "roi": 35.0,
        "risk_level": RiskLevel.high.value,
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "India",
        "website": "https://www.dominos.co.in",
        "contact_email": "dominos.franchise@jublfood.com",
        "description": "Global quick-service pizza leader powered by Jubilant FoodWorks in India with industry-leading 30-minute delivery model.",
        "logo_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=200&q=80",
        "advantages": [
            "Top-tier brand equity & delivery ecosystem",
            "High order volume and high ticket size",
            "Sophisticated POS and mobile app order routing",
        ],
        "disadvantages": [
            "Very high capital investment requirement",
            "Strict multi-unit franchisee qualification criteria",
        ],
        "is_active": True,
    },
]


async def seed_database():
    """Seed sample franchises into database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for data in SAMPLE_FRANCHISES:
            # Check existing franchise
            result = await session.execute(
                select(Franchise).where(Franchise.franchise_name == data["franchise_name"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                franchise = Franchise(**data)
                session.add(franchise)
                logger.info(f"Seeding franchise: {data['franchise_name']}")

        await session.commit()
        logger.info("Database seeding successfully completed! 🎉")


if __name__ == "__main__":
    asyncio.run(seed_database())
