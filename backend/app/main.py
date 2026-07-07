from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.health import dependency_health
from app.core.error_monitoring import ErrorMonitoringMiddleware, error_monitoring_status
from app.core.metrics import MetricsMiddleware, render_metrics
from app.core.observability import RequestIdMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.settings import get_settings
from app.core.tracing import TraceContextMiddleware, tracing_status
from app.db.base import Base
from app.db.session import engine
from app.modules.ai_agents.router import router as ai_agents_router
from app.modules.analytics.router import router as analytics_router
from app.modules.analytics.bi_router import router as bi_router
from app.modules.api_keys.router import router as api_keys_router
from app.modules.auth.router import router as auth_router
from app.modules.byok.router import router as byok_router
from app.modules.integrations.router import router as integrations_router
from app.modules.marketplace.router import router as marketplace_router
from app.modules.scim.router import router as scim_router
from app.modules.sso.router import router as sso_router
from app.modules.audit.router import router as audit_router
from app.modules.comments.router import router as comments_router
from app.modules.decisions.router import router as decisions_router
from app.modules.billing.router import router as billing_router
from app.modules.documents.router import router as documents_router
from app.modules.feedback.router import router as feedback_router
from app.modules.meetings.router import router as meetings_router
from app.modules.notifications.router import router as notifications_router
from app.modules.projects.router import router as projects_router
from app.modules.questions.router import router as questions_router
from app.modules.rag.router import router as rag_router
from app.modules.realtime.websocket import router as realtime_router
from app.modules.rules_ledger.router import router as rules_router
from app.modules.search.router import router as search_router
from app.modules.usage.router import router as usage_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(ErrorMonitoringMiddleware, settings=settings)
app.add_middleware(TraceContextMiddleware)
app.add_middleware(RateLimitMiddleware, settings=settings)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/dependencies", tags=["system"])
def health_dependencies() -> dict:
    return dependency_health(settings, engine)


@app.get("/metrics", tags=["system"])
def metrics():
    return render_metrics()


@app.get("/observability/status", tags=["system"])
def observability_status() -> dict:
    return {
        "opentelemetry": tracing_status(),
        "sentry": error_monitoring_status(settings),
        "metrics": {"enabled": True, "endpoint": "/metrics"},
    }


app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(meetings_router, prefix="/api", tags=["meetings"])
app.include_router(rules_router, prefix="/api", tags=["rules-ledger"])
app.include_router(documents_router, prefix="/api", tags=["documents"])
app.include_router(feedback_router, prefix="/api", tags=["feedback"])
app.include_router(questions_router, prefix="/api", tags=["questions"])
app.include_router(decisions_router, prefix="/api", tags=["decisions"])
app.include_router(ai_agents_router, prefix="/api", tags=["ai-agents"])
app.include_router(rag_router, prefix="/api", tags=["rag"])
app.include_router(audit_router, prefix="/api", tags=["audit"])
app.include_router(usage_router, prefix="/api", tags=["usage"])
app.include_router(billing_router, prefix="/api", tags=["billing"])
app.include_router(comments_router, prefix="/api", tags=["comments"])
app.include_router(notifications_router, prefix="/api", tags=["notifications"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(bi_router, prefix="/api", tags=["bi"])
app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(realtime_router, tags=["realtime"])
# P3 — Enterprise
app.include_router(api_keys_router, prefix="/api", tags=["api-keys"])
app.include_router(integrations_router, prefix="/api", tags=["integrations"])
app.include_router(sso_router, prefix="/api", tags=["sso"])
app.include_router(scim_router, tags=["scim"])
app.include_router(byok_router, prefix="/api", tags=["byok"])
app.include_router(marketplace_router, prefix="/api", tags=["marketplace"])


@app.get("/info", tags=["system"])
def instance_info() -> dict:
    """Informações da instância (modo de deployment, nome)."""
    return {
        "app": settings.private_instance_name if settings.deployment_mode == "private" else settings.app_name,
        "version": "0.1.0",
        "deployment_mode": settings.deployment_mode,
        "public_api_enabled": settings.public_api_enabled,
        "llm_provider": settings.llm_provider,
    }
