import secrets
from contextvars import ContextVar
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
span_id_var: ContextVar[str | None] = ContextVar("span_id", default=None)
_span_count = 0
_span_latency_sum = 0.0


def current_trace_id() -> str | None:
    return trace_id_var.get()


def tracing_status() -> dict:
    return {
        "enabled": True,
        "span_count": _span_count,
        "avg_span_latency_ms": (_span_latency_sum / _span_count * 1000) if _span_count else 0,
    }


class TraceContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        global _span_count, _span_latency_sum
        incoming = request.headers.get("traceparent", "")
        trace_id = secrets.token_hex(16)
        if incoming.startswith("00-"):
            parts = incoming.split("-")
            if len(parts) >= 4 and len(parts[1]) == 32:
                trace_id = parts[1]
        span_id = secrets.token_hex(8)
        trace_token = trace_id_var.set(trace_id)
        span_token = span_id_var.set(span_id)
        started = perf_counter()
        try:
            response = await call_next(request)
        finally:
            elapsed = perf_counter() - started
            _span_count += 1
            _span_latency_sum += elapsed
            trace_id_var.reset(trace_token)
            span_id_var.reset(span_token)
        response.headers["traceparent"] = f"00-{trace_id}-{span_id}-01"
        return response
