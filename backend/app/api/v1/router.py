"""
STARTWISE AI — Main API Router (v1)
Aggregates all endpoint routers for authentication, users, startups, and admin panel.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, startups, predictions, ml, franchises, recommendations, marketing, dashboard, admin, explainability

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(startups.router, prefix="/startups", tags=["Startups"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(ml.router, prefix="/ml", tags=["ML Engine Health"])
api_router.include_router(franchises.router)
api_router.include_router(recommendations.router)
api_router.include_router(marketing.router)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(admin.router, tags=["Admin Panel"])
api_router.include_router(explainability.router)

