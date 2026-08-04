"""
STARTWISE AI — Main API Router (v1)
Aggregates all endpoint routers for authentication, users, and startups.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, startups

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(startups.router, prefix="/startups", tags=["Startups"])
