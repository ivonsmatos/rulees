"""
BI Avançado — endpoints de Business Intelligence para enterprise.

Métricas:
- rules_velocity: regras aprovadas por semana
- compliance_score: % de regras compliant ao longo do tempo
- adoption: usuários ativos, reuniões por mês
- quality_trends: evolução do quality_score médio
- gap_analysis: projetos com mais questões abertas
- decision_coverage: decisões x regras geradas
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.meetings.models import Meeting
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule
from app.modules.decisions.models import Decision

router = APIRouter(prefix="/analytics/bi", tags=["bi"])


@router.get("/rules-velocity")
def rules_velocity(
    weeks: int = Query(default=12, ge=1, le=52),
    project_id: str | None = Query(default=None),
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Regras aprovadas por semana nas últimas N semanas."""
    require_permission(context, "analytics.view")
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)

    q = select(BusinessRule).where(
        BusinessRule.tenant_id == context.tenant_id,
        BusinessRule.status == "approved",
        BusinessRule.created_at >= cutoff,
    )
    if project_id:
        q = q.where(BusinessRule.project_id == project_id)

    rules = list(db.scalars(q))
    # agrupar por semana
    weekly: dict[str, int] = {}
    for rule in rules:
        dt = rule.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        week_label = dt.strftime("%Y-W%W")
        weekly[week_label] = weekly.get(week_label, 0) + 1

    # garantir semanas sem regras
    now = datetime.now(timezone.utc)
    for i in range(weeks):
        w = (now - timedelta(weeks=i)).strftime("%Y-W%W")
        weekly.setdefault(w, 0)

    sorted_weeks = sorted(weekly.keys())
    return {
        "weeks": sorted_weeks,
        "counts": [weekly[w] for w in sorted_weeks],
        "total": sum(weekly.values()),
    }


@router.get("/compliance-score")
def compliance_score(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Score de conformidade: % regras approved/total por projeto."""
    require_permission(context, "analytics.view")
    rows = list(db.execute(
        select(
            BusinessRule.project_id,
            func.count(BusinessRule.id).label("total"),
            func.sum(
                case((BusinessRule.status == "approved", 1), else_=0)
            ).label("approved"),
        )
        .where(BusinessRule.tenant_id == context.tenant_id)
        .group_by(BusinessRule.project_id)
    ))

    projects_data = []
    for row in rows:
        project = db.get(Project, row.project_id)
        pct = round((row.approved / row.total * 100) if row.total else 0, 1)
        projects_data.append({
            "project_id": row.project_id,
            "project_name": project.name if project else row.project_id,
            "total_rules": row.total,
            "approved_rules": row.approved,
            "compliance_pct": pct,
        })

    overall = (
        round(
            sum(p["approved_rules"] for p in projects_data)
            / max(sum(p["total_rules"] for p in projects_data), 1) * 100,
            1,
        )
        if projects_data
        else 0.0
    )
    return {"overall_compliance_pct": overall, "by_project": projects_data}


@router.get("/adoption")
def adoption_metrics(
    months: int = Query(default=6, ge=1, le=24),
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Métricas de adoção: reuniões e usuários ativos por mês."""
    require_permission(context, "analytics.view")
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)

    meetings = list(db.scalars(
        select(Meeting).where(
            Meeting.tenant_id == context.tenant_id,
            Meeting.created_at >= cutoff,
        )
    ))
    monthly: dict[str, dict] = {}
    for m in meetings:
        dt = m.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        label = dt.strftime("%Y-%m")
        bucket = monthly.setdefault(label, {"meetings": 0, "unique_creators": set()})
        bucket["meetings"] += 1
        bucket["unique_creators"].add(m.created_by)

    result = sorted(
        [
            {
                "month": k,
                "meetings": v["meetings"],
                "unique_active_users": len(v["unique_creators"]),
            }
            for k, v in monthly.items()
        ],
        key=lambda x: x["month"],
    )
    return {"months": result, "total_meetings": len(meetings)}


@router.get("/quality-trends")
def quality_trends(
    weeks: int = Query(default=12, ge=1, le=52),
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Evolução do quality_score médio das regras ao longo do tempo."""
    require_permission(context, "analytics.view")
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    rules = list(db.scalars(
        select(BusinessRule).where(
            BusinessRule.tenant_id == context.tenant_id,
            BusinessRule.created_at >= cutoff,
        )
    ))
    weekly_scores: dict[str, list[float]] = {}
    for rule in rules:
        dt = rule.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        label = dt.strftime("%Y-W%W")
        score = getattr(rule, "quality_score", None)
        if score is not None:
            weekly_scores.setdefault(label, []).append(float(score))

    result = sorted(
        [
            {"week": k, "avg_quality": round(sum(v) / len(v), 2), "count": len(v)}
            for k, v in weekly_scores.items()
        ],
        key=lambda x: x["week"],
    )
    return {"trends": result}


@router.get("/gap-analysis")
def gap_analysis(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Projetos com mais questões abertas (lacunas)."""
    require_permission(context, "analytics.view")
    rows = list(db.execute(
        select(
            OpenQuestion.project_id,
            func.count(OpenQuestion.id).label("open_questions"),
        )
        .where(
            OpenQuestion.tenant_id == context.tenant_id,
            OpenQuestion.status == "open",
        )
        .group_by(OpenQuestion.project_id)
        .order_by(func.count(OpenQuestion.id).desc())
    ))
    result = []
    for row in rows:
        project = db.get(Project, row.project_id)
        result.append({
            "project_id": row.project_id,
            "project_name": project.name if project else row.project_id,
            "open_questions": row.open_questions,
        })
    return {"projects": result}


@router.get("/decision-coverage")
def decision_coverage(
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    """Decisões tomadas vs. regras geradas por projeto."""
    require_permission(context, "analytics.view")
    rules_rows = list(db.execute(
        select(BusinessRule.project_id, func.count(BusinessRule.id).label("cnt"))
        .where(BusinessRule.tenant_id == context.tenant_id)
        .group_by(BusinessRule.project_id)
    ))
    decisions_rows = list(db.execute(
        select(Decision.project_id, func.count(Decision.id).label("cnt"))
        .where(Decision.tenant_id == context.tenant_id)
        .group_by(Decision.project_id)
    ))

    rules_map = {r.project_id: r.cnt for r in rules_rows}
    decisions_map = {r.project_id: r.cnt for r in decisions_rows}
    all_projects = set(rules_map) | set(decisions_map)

    result = []
    for pid in all_projects:
        project = db.get(Project, pid)
        r_cnt = rules_map.get(pid, 0)
        d_cnt = decisions_map.get(pid, 0)
        ratio = round(d_cnt / r_cnt, 2) if r_cnt else 0.0
        result.append({
            "project_id": pid,
            "project_name": project.name if project else pid,
            "rules": r_cnt,
            "decisions": d_cnt,
            "decision_to_rule_ratio": ratio,
        })
    result.sort(key=lambda x: x["rules"], reverse=True)
    return {"coverage": result}
