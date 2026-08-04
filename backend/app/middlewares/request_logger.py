"""
STARTWISE AI — Request Logger Middleware
Logs all incoming requests and response times.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"time={process_time:.2f}ms | "
            f"client={client_ip}"
        )

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
