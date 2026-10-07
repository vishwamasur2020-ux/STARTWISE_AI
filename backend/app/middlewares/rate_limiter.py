"""
STARTWISE AI — Rate Limiter Middleware
Simple in-memory sliding window rate limiter per IP.
"""

import time
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit: int = 100, period: int = 60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.period = period
        self._store: dict[str, deque] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        if client_ip in ("testclient", "test", "127.0.0.1", "localhost", "unknown"):
            return await call_next(request)

        now = time.time()
        window_start = now - self.period

        # Clean expired timestamps
        timestamps = self._store[client_ip]
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        if len(timestamps) >= self.requests_limit:
            retry_after = int(self.period - (now - timestamps[0]))
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_limit - len(timestamps)
        )
        return response
