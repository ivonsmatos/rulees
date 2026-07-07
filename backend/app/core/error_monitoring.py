import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.settings import Settings
from app.core.tracing import current_trace_id

logger = logging.getLogger("rulees.error_monitoring")
_captured_errors = 0


def error_monitoring_status(settings: Settings) -> dict:
    return {
        "enabled": bool(settings.sentry_dsn),
        "mode": "sentry" if settings.sentry_dsn else "local",
        "captured_errors": _captured_errors,
    }


class ErrorMonitoringMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        global _captured_errors
        try:
            return await call_next(request)
        except Exception:
            _captured_errors += 1
            logger.exception(
                "Unhandled request error",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "trace_id": current_trace_id(),
                    "sentry_configured": bool(self.settings.sentry_dsn),
                },
            )
            raise
