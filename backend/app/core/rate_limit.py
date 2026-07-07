from collections import defaultdict, deque
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.settings import Settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings
        self.buckets: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.settings.rate_limit_enabled or request.url.path in {"/health", "/metrics"}:
            return await call_next(request)

        identifier = request.headers.get("authorization")
        if identifier is None:
            identifier = request.client.host if request.client else "unknown"
        now = time()
        bucket = self.buckets[identifier]
        window_start = now - self.settings.rate_limit_window_seconds
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.settings.rate_limit_requests:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.settings.rate_limit_window_seconds)},
            )

        bucket.append(now)
        return await call_next(request)
