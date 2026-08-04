"""
STARTWISE AI — Backend Entry Point
Run with: uvicorn run:app --reload
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings

    uvicorn.run(
        "run:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
