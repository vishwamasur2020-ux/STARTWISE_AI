"""
STARTWISE AI — Structured Logging Configuration
Uses Python's logging with JSON-formatted output for production.
"""

import logging
import logging.config
import os
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure application-wide structured logging."""
    os.makedirs("logs", exist_ok=True)

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "logging.Formatter",
                "fmt": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","line":%(lineno)d,"message":"%(message)s"}',
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "standard",
                "level": settings.LOG_LEVEL,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": settings.LOG_FILE,
                "maxBytes": 10_485_760,  # 10 MB
                "backupCount": 5,
                "formatter": "json",
                "level": settings.LOG_LEVEL,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(log_config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
