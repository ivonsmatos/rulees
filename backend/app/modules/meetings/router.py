import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict, not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.billing.service import ensure_billing_limit
from app.modules.auth.models import TenantMember
from app.modules.decisions.models import Decision
from app.modules.meetings.lifecycle import finish_meeting, pause_meeting, resume_meeting, start_meeting
from app.modules.meetings.models import (
    ConsentRecord,
    Meeting,
    MeetingLifecycleEvent,
    MeetingParticipant,
    TranscriptChunk,
)
from app.modules.meetings.schemas import (
    ConsentCreate,
    ConsentRevokeCreate,
    ConsentResponse,
    MeetingFromTemplateCreate,
    MeetingLifecycleEventResponse,
    MeetingCreate,
    MeetingParticipantCreate,
    MeetingParticipantResponse,
    MeetingResponse,
    MeetingSummaryResponse,
    MeetingStateResponse,
    MeetingTemplateResponse,
)
from app.modules.permissions.service import require_permission
from app.modules.projects.models import Project
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule
from app.modules.usage.service import write_usage_event

router = APIRouter()

MEETING_TEMPLATES = [
    {
        "key": "discovery",
        "title": "Descoberta de requisitos",
        "objective": "Mapear contexto, objetivos, dores e lacunas abertas.",
        "agenda": ["Contexto do processo", "Regras atuais", "Excecoes", "Duvidas e proximos passos"],
    },
    {
        "key": "rules_validation",
        "title": "Validacao de regras",
        "objective": "Validar regras detectadas, conflitos e evidencias antes de aprovacao.",
        "agenda": ["Regras propostas", "Evidencias", "Conflitos", "Aprovacoes e rejeicoes"],
    },
    {
        "key": "tech_handoff",
        "title": "Handoff tecnico",
        "objective": "Converter decisoes e regras aprovadas em insumos para desenvolvimento.",
        "agenda": ["Resumo funcional", "Dependencias", "Criterios de aceite", "Pendencias"],
    },
]


def _get_tenant_project(db: Session, context: RequestContext, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != context.tenant_id:
        raise not_found("Project not found")
    return project


def _get_tenant_meeting(db: Session, context: RequestContext, meeting_id: str) -> Meeting:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.tenant_id != context.tenant_id:
        raise not_found("Meeting not found")
    return meeting


def _write_lifecycle_event(
    db: Session,
    *,
    meeting: Meeting,
    user_id: str,
    event_type: str,
    from_status: str | None = None,
    to_status: str | None = None,
    details: dict | None = None,
) -> MeetingLifecycleEvent:
    event = MeetingLifecycleEvent(
        tenant_id=meeting.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=user_id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        details=json.dumps(details or {}),
    )
    db.add(event)
    return event


def _lifecycle_response(event: MeetingLifecycleEvent) -> MeetingLifecycleEventResponse:
    return MeetingLifecycleEventResponse(
        id=event.id,
        tenant_id=event.tenant_id,
        project_id=event.project_id,
        meeting_id=event.meeting_id,
        user_id=event.user_id,
        event_type=event.event_type,
        from_status=event.from_status,
        to_status=event.to_status,
        details=json.loads(event.details or "{}"),
        created_at=event.created_at,
    )


def _ensure_meeting_participant(
    db: Session,
    *,
    meeting: Meeting,
    user_id: str,
    role: str,
    created_by: str,
    consent_required: bool = True,
) -> MeetingParticipant:
    existing = db.scalar(
        select(MeetingParticipant).where(
            MeetingParticipant.meeting_id == meeting.id,
            MeetingParticipant.user_id == user_id,
        )
    )
    if existing:
        return existing
    participant = MeetingParticipant(
        tenant_id=meeting.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=user_id,
        role=role,
        created_by=created_by,
        consent_required=consent_required,
    )
    db.add(participant)
    return participant


@router.get("/projects/{project_id}/meetings", response_model=list[MeetingResponse])
def list_meetings(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[Meeting]:
    require_permission(context, "meeting.view")
    _get_tenant_project(db, context, project_id)
    return list(
        db.scalars(
            select(Meeting)
            .where(Meeting.tenant_id == context.tenant_id, Meeting.project_id == project_id)
            .order_by(Meeting.created_at.desc())
        )
    )


@router.post("/projects/{project_id}/meetings", response_model=MeetingResponse)
def create_meeting(
    project_id: str,
    payload: MeetingCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.create")
    _get_tenant_project(db, context, project_id)
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="meeting_created")
    meeting = Meeting(
        tenant_id=context.tenant_id,
        project_id=project_id,
        title=payload.title.strip(),
        objective=payload.objective.strip(),
        created_by=context.user_id,
    )
    db.add(meeting)
    db.flush()
    _ensure_meeting_participant(
        db,
        meeting=meeting,
        user_id=context.user_id,
        role="owner",
        created_by=context.user_id,
    )
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.created",
        to_status=meeting.status,
        details={"title": meeting.title},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.create",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_created",
        details={"meeting_title": meeting.title},
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/meetings/templates", response_model=list[MeetingTemplateResponse])
def list_meeting_templates(
    context: RequestContext = Depends(get_request_context),
) -> list[dict]:
    require_permission(context, "meeting.view")
    return MEETING_TEMPLATES


@router.post("/projects/{project_id}/meetings/from-template", response_model=MeetingResponse)
def create_meeting_from_template(
    project_id: str,
    payload: MeetingFromTemplateCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.create")
    _get_tenant_project(db, context, project_id)
    template = next((item for item in MEETING_TEMPLATES if item["key"] == payload.template_key), None)
    if template is None:
        raise not_found("Meeting template not found")
    ensure_billing_limit(db, tenant_id=context.tenant_id, event_type="meeting_created")
    meeting = Meeting(
        tenant_id=context.tenant_id,
        project_id=project_id,
        title=(payload.title or template["title"]).strip(),
        objective=f"{template['objective']}\n\nAgenda:\n- " + "\n- ".join(template["agenda"]),
        created_by=context.user_id,
    )
    db.add(meeting)
    db.flush()
    _ensure_meeting_participant(
        db,
        meeting=meeting,
        user_id=context.user_id,
        role="owner",
        created_by=context.user_id,
    )
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.created_from_template",
        to_status=meeting.status,
        details={"template_key": payload.template_key},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.create_from_template",
        resource_type="meeting",
        resource_id=meeting.id,
        details={"template_key": payload.template_key},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_created",
        details={"meeting_title": meeting.title, "template_key": payload.template_key},
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.post("/meetings/{meeting_id}/consent", response_model=ConsentResponse)
def accept_consent(
    meeting_id: str,
    payload: ConsentCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ConsentRecord:
    require_permission(context, "meeting.consent.accept")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    existing = db.scalars(
        select(ConsentRecord)
        .where(
            ConsentRecord.meeting_id == meeting.id,
            ConsentRecord.user_id == context.user_id,
            ConsentRecord.revoked_at.is_(None),
        )
        .order_by(ConsentRecord.accepted_at.desc())
    ).first()
    if existing:
        return existing
    consent = ConsentRecord(
        tenant_id=context.tenant_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        text_version=payload.text_version,
        accepted_scope=json.dumps(payload.accepted_scope),
    )
    db.add(consent)
    _ensure_meeting_participant(
        db,
        meeting=meeting,
        user_id=context.user_id,
        role="participant",
        created_by=context.user_id,
    )
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="consent.accepted",
        from_status=meeting.status,
        to_status=meeting.status,
        details={"text_version": payload.text_version},
    )
    db.flush()
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.consent.accept",
        resource_type="meeting",
        resource_id=meeting.id,
        details={"text_version": payload.text_version},
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="consent_accepted",
        details={"text_version": payload.text_version},
    )
    db.commit()
    db.refresh(consent)
    return consent


@router.post("/meetings/{meeting_id}/consent/revoke", response_model=ConsentResponse)
def revoke_consent(
    meeting_id: str,
    payload: ConsentRevokeCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> ConsentRecord:
    require_permission(context, "meeting.consent.revoke")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    if meeting.status == "active":
        raise conflict("Consent cannot be revoked while meeting is active")
    consent = db.scalars(
        select(ConsentRecord)
        .where(
            ConsentRecord.meeting_id == meeting.id,
            ConsentRecord.user_id == context.user_id,
            ConsentRecord.revoked_at.is_(None),
        )
        .order_by(ConsentRecord.accepted_at.desc())
    ).first()
    if consent is None:
        raise not_found("Active consent not found")
    consent.revoked_at = datetime.now(timezone.utc)
    consent.revoked_by = context.user_id
    consent.revoke_reason = payload.reason.strip() or None
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="consent.revoked",
        from_status=meeting.status,
        to_status=meeting.status,
        details={"reason": consent.revoke_reason},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.consent.revoke",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    db.commit()
    db.refresh(consent)
    return consent


@router.get("/meetings/{meeting_id}/participants", response_model=list[MeetingParticipantResponse])
def list_participants(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[MeetingParticipant]:
    require_permission(context, "meeting.participant.view")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    return list(
        db.scalars(
            select(MeetingParticipant)
            .where(MeetingParticipant.tenant_id == context.tenant_id, MeetingParticipant.meeting_id == meeting.id)
            .order_by(MeetingParticipant.created_at.asc())
        )
    )


@router.post("/meetings/{meeting_id}/participants", response_model=MeetingParticipantResponse)
def add_participant(
    meeting_id: str,
    payload: MeetingParticipantCreate,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MeetingParticipant:
    require_permission(context, "meeting.participant.manage")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    tenant_member = db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == context.tenant_id,
            TenantMember.user_id == payload.user_id,
        )
    )
    if tenant_member is None:
        raise bad_request("User must be a tenant member before joining a meeting")
    participant = _ensure_meeting_participant(
        db,
        meeting=meeting,
        user_id=payload.user_id,
        role=payload.role,
        consent_required=payload.consent_required,
        created_by=context.user_id,
    )
    participant.role = payload.role
    participant.consent_required = payload.consent_required
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="participant.added",
        from_status=meeting.status,
        to_status=meeting.status,
        details={"participant_user_id": payload.user_id, "role": payload.role},
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.participant.manage",
        resource_type="meeting",
        resource_id=meeting.id,
        details={"participant_user_id": payload.user_id, "role": payload.role},
    )
    db.commit()
    db.refresh(participant)
    return participant


@router.get("/meetings/{meeting_id}/lifecycle-events", response_model=list[MeetingLifecycleEventResponse])
def list_lifecycle_events(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[MeetingLifecycleEventResponse]:
    require_permission(context, "meeting.lifecycle.view")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    events = list(
        db.scalars(
            select(MeetingLifecycleEvent)
            .where(MeetingLifecycleEvent.tenant_id == context.tenant_id, MeetingLifecycleEvent.meeting_id == meeting.id)
            .order_by(MeetingLifecycleEvent.created_at.asc())
        )
    )
    return [_lifecycle_response(event) for event in events]


@router.post("/meetings/{meeting_id}/start", response_model=MeetingResponse)
def start(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.start")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    from_status = meeting.status
    meeting = start_meeting(db, meeting)
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.started",
        from_status=from_status,
        to_status=meeting.status,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.start",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_started",
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.post("/meetings/{meeting_id}/pause", response_model=MeetingResponse)
def pause(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.pause")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    from_status = meeting.status
    meeting = pause_meeting(meeting)
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.paused",
        from_status=from_status,
        to_status=meeting.status,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.pause",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_paused",
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.post("/meetings/{meeting_id}/resume", response_model=MeetingResponse)
def resume(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.resume")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    from_status = meeting.status
    meeting = resume_meeting(db, meeting)
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.resumed",
        from_status=from_status,
        to_status=meeting.status,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.resume",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_resumed",
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.post("/meetings/{meeting_id}/finish", response_model=MeetingResponse)
def finish(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> Meeting:
    require_permission(context, "meeting.finish")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    from_status = meeting.status
    meeting = finish_meeting(meeting)
    _write_lifecycle_event(
        db,
        meeting=meeting,
        user_id=context.user_id,
        event_type="meeting.finished",
        from_status=from_status,
        to_status=meeting.status,
    )
    write_audit_log(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        action="meeting.finish",
        resource_type="meeting",
        resource_id=meeting.id,
    )
    write_usage_event(
        db,
        tenant_id=context.tenant_id,
        project_id=meeting.project_id,
        meeting_id=meeting.id,
        user_id=context.user_id,
        event_type="meeting_finished",
    )
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/meetings/{meeting_id}/state", response_model=MeetingStateResponse)
def state(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MeetingStateResponse:
    require_permission(context, "meeting.view")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    consent = db.scalars(
        select(ConsentRecord)
        .where(
            ConsentRecord.meeting_id == meeting.id,
            ConsentRecord.user_id == context.user_id,
            ConsentRecord.revoked_at.is_(None),
        )
        .order_by(ConsentRecord.accepted_at.desc())
    ).first()
    has_consent = consent is not None
    participants = list(
        db.scalars(
            select(MeetingParticipant)
            .where(MeetingParticipant.tenant_id == context.tenant_id, MeetingParticipant.meeting_id == meeting.id)
            .order_by(MeetingParticipant.created_at.asc())
        )
    )
    lifecycle_events = list(
        db.scalars(
            select(MeetingLifecycleEvent)
            .where(MeetingLifecycleEvent.tenant_id == context.tenant_id, MeetingLifecycleEvent.meeting_id == meeting.id)
            .order_by(MeetingLifecycleEvent.created_at.asc())
        )
    )
    transcript = list(
        db.scalars(
            select(TranscriptChunk)
            .where(
                TranscriptChunk.tenant_id == context.tenant_id,
                TranscriptChunk.meeting_id == meeting.id,
            )
            .order_by(TranscriptChunk.created_at.asc())
        )
    )
    rules = list(
        db.scalars(
            select(BusinessRule)
            .where(BusinessRule.tenant_id == context.tenant_id, BusinessRule.meeting_id == meeting.id)
            .order_by(BusinessRule.created_at.desc())
        )
    )
    questions = list(
        db.scalars(
            select(OpenQuestion)
            .where(OpenQuestion.tenant_id == context.tenant_id, OpenQuestion.meeting_id == meeting.id)
            .order_by(OpenQuestion.created_at.desc())
        )
    )
    decisions = list(
        db.scalars(
            select(Decision)
            .where(Decision.tenant_id == context.tenant_id, Decision.meeting_id == meeting.id)
            .order_by(Decision.created_at.desc())
        )
    )
    return MeetingStateResponse(
        meeting=meeting,
        has_consent=has_consent,
        consent=consent,
        participants=participants,
        lifecycle_events=[_lifecycle_response(event) for event in lifecycle_events],
        transcript=transcript,
        rules=[
            {
                "id": rule.id,
                "code": rule.code,
                "rule_text": rule.rule_text,
                "status": rule.status,
                "confidence_score": rule.confidence_score,
                "quality_score": rule.quality_score,
                "source_chunk_ids": json.loads(rule.source_chunk_ids),
            }
            for rule in rules
        ],
        questions=[
            {
                "id": question.id,
                "question_text": question.question_text,
                "reason": question.reason,
                "gap_type": question.gap_type,
                "priority": question.priority,
                "status": question.status,
                "confidence_score": question.confidence_score,
                "source_chunk_ids": json.loads(question.source_chunk_ids),
            }
            for question in questions
        ],
        decisions=[
            {
                "id": decision.id,
                "decision_text": decision.decision_text,
                "decision_type": decision.decision_type,
                "status": decision.status,
                "responsible_area": decision.responsible_area,
                "confidence_score": decision.confidence_score,
                "source_chunk_ids": json.loads(decision.source_chunk_ids),
            }
            for decision in decisions
        ],
    )


@router.get("/meetings/{meeting_id}/summary", response_model=MeetingSummaryResponse)
def meeting_summary(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> MeetingSummaryResponse:
    require_permission(context, "meeting.view")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    transcript_count = db.scalar(
        select(func.count(TranscriptChunk.id)).where(
            TranscriptChunk.tenant_id == context.tenant_id,
            TranscriptChunk.meeting_id == meeting.id,
        )
    ) or 0
    rules = list(
        db.scalars(
            select(BusinessRule).where(
                BusinessRule.tenant_id == context.tenant_id,
                BusinessRule.meeting_id == meeting.id,
            )
        )
    )
    questions = list(
        db.scalars(
            select(OpenQuestion).where(
                OpenQuestion.tenant_id == context.tenant_id,
                OpenQuestion.meeting_id == meeting.id,
                OpenQuestion.status == "open",
            )
        )
    )
    decisions_count = db.scalar(
        select(func.count(Decision.id)).where(
            Decision.tenant_id == context.tenant_id,
            Decision.meeting_id == meeting.id,
        )
    ) or 0
    approved_count = len([rule for rule in rules if rule.status == "approved"])
    next_steps: list[str] = []
    if questions:
        next_steps.append(f"Responder {len(questions)} duvidas abertas antes do handoff.")
    if approved_count < len(rules):
        next_steps.append("Revisar regras pendentes/conflitantes no Rules Ledger.")
    if transcript_count == 0:
        next_steps.append("Adicionar transcricao ou audio para gerar evidencias.")
    if not next_steps:
        next_steps.append("Gerar ou revisar documento funcional final.")
    summary = (
        f"A reuniao '{meeting.title}' tem {transcript_count} trechos de transcricao, "
        f"{len(rules)} regras detectadas ({approved_count} aprovadas), "
        f"{len(questions)} duvidas abertas e {decisions_count} decisoes registradas."
    )
    return MeetingSummaryResponse(
        meeting_id=meeting.id,
        title=meeting.title,
        status=meeting.status,
        transcript_chunks=int(transcript_count),
        rules_total=len(rules),
        rules_approved=approved_count,
        open_questions=len(questions),
        decisions_total=int(decisions_count),
        summary=summary,
        next_steps=next_steps,
    )
