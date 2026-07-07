from dataclasses import dataclass
import socket
import time
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.settings import Settings


@dataclass(frozen=True)
class ComponentHealth:
    name: str
    status: str
    latency_ms: float
    details: dict[str, str]


def _check_database(engine: Engine) -> ComponentHealth:
    started_at = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        return ComponentHealth(
            name="database",
            status="ok",
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"dialect": engine.dialect.name},
        )
    except Exception as exc:
        return ComponentHealth(
            name="database",
            status="error",
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"error": exc.__class__.__name__},
        )


def _check_redis(redis_url: str) -> ComponentHealth:
    started_at = time.perf_counter()
    parsed = urlparse(redis_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 6379
    try:
        with socket.create_connection((host, port), timeout=1.5) as sock:
            sock.settimeout(1.5)
            sock.sendall(b"*1\r\n$4\r\nPING\r\n")
            response = sock.recv(16)
        status = "ok" if response.startswith(b"+PONG") else "error"
        return ComponentHealth(
            name="redis",
            status=status,
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"host": host, "port": str(port)},
        )
    except Exception as exc:
        return ComponentHealth(
            name="redis",
            status="error",
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"host": host, "port": str(port), "error": exc.__class__.__name__},
        )


def _check_storage(settings: Settings) -> ComponentHealth:
    started_at = time.perf_counter()
    try:
        path = settings.resolved_storage_path
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".rulees-health"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return ComponentHealth(
            name="storage",
            status="ok",
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"path": str(path)},
        )
    except Exception as exc:
        return ComponentHealth(
            name="storage",
            status="error",
            latency_ms=round((time.perf_counter() - started_at) * 1000, 2),
            details={"error": exc.__class__.__name__},
        )


def dependency_health(settings: Settings, engine: Engine) -> dict:
    components = [
        _check_database(engine),
        _check_redis(settings.redis_url),
        _check_storage(settings),
    ]
    overall = "ok" if all(component.status == "ok" for component in components) else "degraded"
    return {
        "status": overall,
        "service": settings.app_name,
        "environment": settings.environment,
        "components": [
            {
                "name": component.name,
                "status": component.status,
                "latency_ms": component.latency_ms,
                "details": component.details,
            }
            for component in components
        ],
    }
