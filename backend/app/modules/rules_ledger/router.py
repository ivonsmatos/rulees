from datetime import datetime, timezone
from difflib import ndiff
import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.billing.service import ensure_billing_limit
from app.modules.ai_agents.service import write_agent_run
from app.modules.meetings.models import TranscriptChunk
from app.modules.meetings.schemas import TranscriptChunkResponse
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.rag.service import check_rule_conflicts, upsert_embedding
from app.modules.rules_ledger.models import BusinessRule, RuleLifecycleEvent, RuleVersion
from app.modules.rules_ledger.schemas import (
    RuleLifecycleAction,
    RuleLifecycleEventResponse,
    RuleReplaceCreate,
    RuleResponse,
    RuleVersionCreate,
    RuleVersionDiffResponse,
    RuleVersionResponse,
)
from app.modules.rules_ledger.service import (
    approve_rule,
    calculate_rule_quality_details,
    create_rule_version,
    reject_rule,
    revise_rule,
    serialize_quality_details,
    write_rule_lifecycle_event,
)
from app.modules.usage.service import write_usage_event

router = APIRouter()


def _get_rule(db: Session, context: RequestContext, rule_id: str) -> BusinessRule:
    rule = db.get(BusinessRule, rule_id)
    if rule is None or rule.tenant_id != context.tenant_id:
        raise not_found("Rule not found")
    return rule


def _source_chunk_ids(rule: BusinessRule) -> list[str]:
    try:
        parsed = json.loads(rule.source_chunk_ids)
    except json.JSONDecodeError:
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def _ensure_quality_details(rule: BusinessRule) -> None:
    if rule.quality_details and rule.quality_details != "{}":
        return
    details = calculate_rule_quality_details(
        rule_text=rule.rule_text,
        condition_text=rule.condition_text,
        result_text=rule.result_text,
        source_chunk_ids=_source_chunk_ids(rule),
        confidence_score=rule.confidence_score,
    )
    rule.quality_score = details["score"]
    rule.quality_details = serialize_quality_details(details)


def _diff_lines(left: str, right: str) -> list[dict]:
    lines = []
    for line in ndiff(left.splitlines(), right.splitlines()):
        marker = line[:2]
        if marker == "  ":
            kind = "context"
        elif marker == "- ":
            kind = "removed"
        elif marker == "+ ":
            kind = "added"
        else:
            continue
        lines.append({"kind": kind, "text": line[2:]})
    return lines[:500]


@router.get("/projects/{project_id}/rules", response_model=list[RuleResponse])
def list_rules(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[BusinessRule]:
    require_permission(context, "rule.view")
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != context.tenant_id:
        raise not_found("Project not found")
    rules = list(
        db.scalars(
            select(BusinessRule)
            .where(BusinessRule.tenant_id == context.tenant_id, BusinessRule.project_id == project_id)
            .order_by(BusinessRule.created_at.desc())
        )
    )
    for rule in rules:
        _ensure_quality_details(rule)
    return rules


@router.get("/rules/{rule_id}/versions", response_model=list[RuleVersionResponse])
def list_rule_versions(
    rule_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[RuleVersion]:
    require_permission(context, "rule.version.view")
    rule = _get_rule(db, context, rule_id)
    return list(
        db.scalars(
            select(RuleVersion)
            .where(RuleVersion.tenant_id == context.tenant_id, RuleVersion.rule_id == rule.id)
            .order_by(RuleVersion.version_number.desc(), RuleVersion.created_at.desc())
        )
    )


@router.get("/rules/{rule_id}/evidence", response_model=list[TranscriptChunkResponse])
def list_rule_evidence(
    rule_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[TranscriptChunk]:
    require_permission(context, "rule.view")
    rule = _get_rule(db, context, rule_id)
    chunk_ids = _source_chunk_ids(rule)
    if not chunk_ids:
        return []
    return list(
        db.scalars(
            select(TranscriptChunk)
            .where(TranscriptChunk.tenant_id == context.tenant_id, TranscriptChunk.id.in_(chunk_ids))
            .order_by(TranscriptChunk.created_at.asc())
        )
    )


@router.get("/rules/{rule_id}/versions/diff", response_model=RuleVersionDiffResponse)
def rule_version_diff(
    rule_id: str,
    from_version: int,
    to_version: int,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> RuleVersionDiffResponse:
    require_permission(context, "rule.version.view")
    rule = _get_rule(db, context, rule_id)
    versions = list(
        db.scalars(
            select(RuleVersion).where(
                RuleVersion.tenant_id == context.tenant_id,
                RuleVersion.rule_id == rule.id,
                RuleVersion.version_number.in_([from_version, to_version]),
            )
        )
    )
    by_number = {version.version_number: version for version in versions}
    if from_version not in by_number or to_version not in by_number:
        raise not_found("Version not found")
    return RuleVersionDiffResponse(
        resource_type="business_rule",
        resource_id=rule.id,
        from_version=from_version,
        to_version=to_version,
        lines=_diff_lines(by_number[from_version].rule_text, by_number[to_version].rule_text),
    )


@router.get("/rules/{rule_id}/lifecycle-events", response_model=list[RuleLifecycleEventResponse])
def list_rule_lifecycle_events(
    rule_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[RuleLifecycleEvent]:
    require_permission(context, "rule.version.view")
    rule = _get_rule(db, context, rule_id)
    return list(
        db.scalars(
            select(RuleLifecycleEvent)
            .where(RuleLifecycleEvent.tenant_id == context.tenant_id, RuleLifecycleEvent.rule_id == rule.id)
            .order_by(RuleLifecycleEvent.created_at.asc())
        )
    )


@router.post("/rules/{rule_id}/versions", response_model=RuleResponse)
def create_version(
    rule_id: str,
    payload: RuleVersionCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.version.create")
    rule = _get_rule(db, context, rule_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="rule_version_created")
    from_status = rule.status
    revise_rule(
        rule,
        rule_text=payload.rule_text,
        condition_text=payload.condition_text,
        result_text=payload.result_text,
    )
    guardian_result = check_rule_conflicts(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        rule_id=rule.id,
        rule_text=rule.rule_text,
    )
    rule.status = guardian_result.recommended_status
    upsert_embedding(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        source_type="business_rule",
        source_id=rule.id,
        content=rule.rule_text,
    )
    create_rule_version(
        db,
        rule,
        created_by=context.user_id,
        change_reason=payload.change_reason,
    )
    quality_details = json.loads(rule.quality_details) if rule.quality_details else {}
    write_agent_run(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        agent_name="Rule Quality",
        agent_role="rule_quality_scorer",
        input_reference={
            "source_type": "business_rule",
            "source_ids": [rule.id],
        },
        output={
            "score": quality_details.get("score", rule.quality_score),
            "checks": quality_details.get("checks", []),
            "missing": quality_details.get("missing", []),
            "evidence_count": quality_details.get("evidence_count", 0),
        },
        confidence_score=rule.confidence_score,
        metadata={"scoring_method": "deterministic_checklist_v1", "trigger": "manual_revision"},
    )
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.revised",
        from_status=from_status,
        to_status=rule.status,
        details={
            "change_reason": payload.change_reason,
            "version_number": rule.version_number,
            "rag_result_type": guardian_result.result_type,
        },
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.version.create",
        resource_type="business_rule",
        resource_id=rule.id,
        details={
            "code": rule.code,
            "version_number": rule.version_number,
            "rag_result_type": guardian_result.result_type,
        },
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        user_id=context.user_id,
        event_type="rule_version_created",
        details={"code": rule.code, "version_number": rule.version_number},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/approve", response_model=RuleResponse)
def approve(
    rule_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.approve")
    rule = _get_rule(db, context, rule_id)
    from_status = rule.status
    approve_rule(rule, context.user_id)
    create_rule_version(
        db,
        rule,
        created_by=context.user_id,
        change_reason="Aprovacao humana",
    )
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.approved",
        from_status=from_status,
        to_status=rule.status,
        details={"version_number": rule.version_number},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.approve",
        resource_type="business_rule",
        resource_id=rule.id,
        details={"code": rule.code},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        user_id=context.user_id,
        event_type="rule_approved",
        details={"code": rule.code},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/reject", response_model=RuleResponse)
def reject(
    rule_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.reject")
    rule = _get_rule(db, context, rule_id)
    from_status = rule.status
    reject_rule(rule)
    create_rule_version(
        db,
        rule,
        created_by=context.user_id,
        change_reason="Rejeicao humana",
    )
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.rejected",
        from_status=from_status,
        to_status=rule.status,
        details={"version_number": rule.version_number},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.reject",
        resource_type="business_rule",
        resource_id=rule.id,
        details={"code": rule.code},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        user_id=context.user_id,
        event_type="rule_rejected",
        details={"code": rule.code},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/archive", response_model=RuleResponse)
def archive_rule(
    rule_id: str,
    payload: RuleLifecycleAction | None = None,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.archive")
    rule = _get_rule(db, context, rule_id)
    from_status = rule.status
    rule.status = "archived"
    rule.archived_at = datetime.now(timezone.utc)
    create_rule_version(db, rule, created_by=context.user_id, change_reason="Regra arquivada")
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.archived",
        from_status=from_status,
        to_status=rule.status,
        details={"reason": payload.reason if payload else ""},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.archive",
        resource_type="business_rule",
        resource_id=rule.id,
        details={"code": rule.code},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/revoke", response_model=RuleResponse)
def revoke_rule(
    rule_id: str,
    payload: RuleLifecycleAction | None = None,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.revoke")
    rule = _get_rule(db, context, rule_id)
    from_status = rule.status
    rule.status = "revoked"
    rule.revoked_at = datetime.now(timezone.utc)
    create_rule_version(db, rule, created_by=context.user_id, change_reason="Regra revogada")
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.revoked",
        from_status=from_status,
        to_status=rule.status,
        details={"reason": payload.reason if payload else ""},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.revoke",
        resource_type="business_rule",
        resource_id=rule.id,
        details={"code": rule.code},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/rules/{rule_id}/replace", response_model=RuleResponse)
def replace_rule(
    rule_id: str,
    payload: RuleReplaceCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> BusinessRule:
    require_permission(context, "rule.replace")
    rule = _get_rule(db, context, rule_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="rule_version_created")
    replacement_text = payload.rule_text.strip()
    details = calculate_rule_quality_details(
        rule_text=replacement_text,
        condition_text=payload.condition_text,
        result_text=payload.result_text,
        source_chunk_ids=[],
        confidence_score=0.74,
    )
    replacement = BusinessRule(
        code=f"{rule.code}-R",
        tenant_id=rule.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        rule_text=replacement_text,
        condition_text=payload.condition_text.strip() if payload.condition_text else None,
        result_text=payload.result_text.strip() if payload.result_text else None,
        status="needs_review",
        confidence_score=0.74,
        quality_score=details["score"],
        quality_details=serialize_quality_details(details),
        source_chunk_ids="[]",
    )
    db.add(replacement)
    db.flush()
    from_status = rule.status
    rule.status = "replaced"
    rule.replaced_by_rule_id = replacement.id
    create_rule_version(db, rule, created_by=context.user_id, change_reason="Regra substituida")
    create_rule_version(db, replacement, created_by=context.user_id, change_reason=payload.change_reason)
    write_rule_lifecycle_event(
        db,
        rule=rule,
        user_id=context.user_id,
        event_type="rule.replaced",
        from_status=from_status,
        to_status=rule.status,
        details={"replacement_rule_id": replacement.id, "reason": payload.change_reason},
    )
    write_rule_lifecycle_event(
        db,
        rule=replacement,
        user_id=context.user_id,
        event_type="rule.created_as_replacement",
        from_status=None,
        to_status=replacement.status,
        details={"replaces_rule_id": rule.id},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="rule.replace",
        resource_type="business_rule",
        resource_id=rule.id,
        details={"code": rule.code, "replacement_rule_id": replacement.id},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=rule.project_id,
        meeting_id=rule.meeting_id,
        user_id=context.user_id,
        event_type="rule_version_created",
        details={"code": rule.code, "replacement_rule_id": replacement.id},
    )
    db.commit()
    db.refresh(replacement)
    return replacement
