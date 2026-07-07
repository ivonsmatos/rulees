from collections import defaultdict
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

_request_counts: dict[tuple[str, str, int], int] = defaultdict(int)
_request_latency_sum: dict[tuple[str, str], float] = defaultdict(float)
_request_latency_count: dict[tuple[str, str], int] = defaultdict(int)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started = perf_counter()
        response = await call_next(request)
        elapsed = perf_counter() - started
        route = request.url.path
        method = request.method
        _request_counts[(method, route, response.status_code)] += 1
        _request_latency_sum[(method, route)] += elapsed
        _request_latency_count[(method, route)] += 1
        return response


def render_metrics() -> PlainTextResponse:
    lines = [
        "# HELP rulees_http_requests_total Total HTTP requests.",
        "# TYPE rulees_http_requests_total counter",
    ]
    for (method, route, status), count in sorted(_request_counts.items()):
        lines.append(
            f'rulees_http_requests_total{{method="{method}",route="{route}",status="{status}"}} {count}'
        )
    lines.extend(
        [
            "# HELP rulees_http_request_duration_seconds_avg Average request duration.",
            "# TYPE rulees_http_request_duration_seconds_avg gauge",
        ]
    )
    for (method, route), total in sorted(_request_latency_sum.items()):
        count = max(_request_latency_count[(method, route)], 1)
        lines.append(
            f'rulees_http_request_duration_seconds_avg{{method="{method}",route="{route}"}} {total / count:.6f}'
        )
    return PlainTextResponse("\n".join(lines) + "\n")
