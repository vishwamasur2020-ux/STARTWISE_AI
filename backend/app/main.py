"""
STARTWISE AI — FastAPI Application Entry Point
Production-ready configuration with lifespan management and global exception handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppException
from app.database.session import engine, Base
from app.api.v1.router import api_router
from app.middlewares.rate_limiter import RateLimitMiddleware
from app.middlewares.request_logger import RequestLoggerMiddleware

logger = get_logger(__name__)


# ─── Lifespan (startup / shutdown) ──────────────────────────────────────────
from app.core.model_manager import get_model_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize resources on startup, cleanup on shutdown."""
    setup_logging()

    # Initialize ML Engine & Load Trained Models
    try:
        model_manager = get_model_manager()
        model_manager.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize ML Engine: {e}")

    def sync_db_schema(sync_conn):
        from sqlalchemy import inspect
        Base.metadata.create_all(sync_conn)
        inspector = inspect(sync_conn)
        if "marketing_strategies" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("marketing_strategies")]
            if "user_id" not in columns:
                Base.metadata.tables["marketing_strategies"].drop(sync_conn, checkfirst=True)
                Base.metadata.create_all(sync_conn)

    async with engine.begin() as conn:
        await conn.run_sync(sync_db_schema)

    yield

    await engine.dispose()


# ─── App Factory ────────────────────────────────────────────────────────────
def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Intelligent Startup Validation & Franchise Recommendation System",
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Security Middlewares ─────────────────────────────────────────────────
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggerMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=settings.RATE_LIMIT_REQUESTS,
        period=settings.RATE_LIMIT_PERIOD,
    )

    # ── Security Headers Middleware ──────────────────────────────────────────
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # ── Global Exception Handlers ────────────────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_code": exc.error_code, "success": False},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc) if settings.DEBUG else "Internal Server Error", "success": False},
        )

    # ── API Router ───────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    from app.api.v1.endpoints import startups, predictions
    app.include_router(startups.router, prefix="/api/startups", tags=["Startups API"])
    app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions API"])

    # ── Fast Health Check ────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            },
        )

    # ── Detailed Health Check ────────────────────────────────────────────────
    @app.get("/api/health", tags=["Health"])
    @app.get("/api/v1/health", tags=["Health"])
    async def detailed_health_check():
        from sqlalchemy import text
        from app.database.session import AsyncSessionLocal
        from app.core.model_manager import get_model_manager

        # Check DB
        db_status = "healthy"
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # Check ML Models
        mm = get_model_manager()
        ml_status = {
            "success_model": "success" in mm.models,
            "risk_model": "risk" in mm.models,
            "roi_model": "roi" in mm.models,
            "competition_model": "competition" in mm.models,
            "is_loaded": mm.is_loaded,
        }

        # Check XAI Engine
        try:
            import shap
            shap_available = True
            shap_version = getattr(shap, "__version__", "unknown")
        except ImportError:
            shap_available = False
            shap_version = "unavailable"

        overall_healthy = (db_status == "healthy") and mm.is_loaded

        return JSONResponse(
            status_code=200 if overall_healthy else 503,
            content={
                "status": "healthy" if overall_healthy else "degraded",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "services": {
                    "database": db_status,
                    "ml_engine": "healthy" if mm.is_loaded else "degraded",
                    "ml_models": ml_status,
                    "xai_engine": {
                        "status": "healthy" if shap_available else "unavailable",
                        "shap_version": shap_version,
                        "tree_explainer": "online",
                        "linear_explainer": "online",
                    },
                    "email_service": {
                        "status": "enabled" if settings.EMAIL_ENABLED else "disabled",
                        "configured": bool(settings.RESEND_API_KEY and len(settings.RESEND_API_KEY) > 10),
                    },
                    "report_service": {
                        "status": "online",
                        "storage_dir": settings.REPORT_STORAGE_DIR,
                    },
                },
            },
        )

    return app


app = create_application()
