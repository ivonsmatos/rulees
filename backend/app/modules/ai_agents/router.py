from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.ai_agents.models import AgentRun
from app.modules.ai_agents.orchestration import analyze_transcript_text
from app.modules.ai_agents.schemas import AgentRunResponse, TranscriptAnalysisRequest, TranscriptAnalysisResponse
from app.modules.ai_agents.service import agent_run_to_response
from app.modules.meetings.models import Meeting
from app.modules.permissions.service import require_permission

router = APIRouter()


def _get_tenant_meeting(db: Session, context: RequestContext, meeting_id: str) -> Meeting:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.tenant_id != context.tenant_id:
        raise not_found("Meeting not found")
    return meeting


@router.post("/ai-agents/analyze-preview", response_model=TranscriptAnalysisResponse)
def analyze_preview(
    payload: TranscriptAnalysisRequest,
    context: RequestContext = Depends(get_request_context),
) -> TranscriptAnalysisResponse:
    """
    Classifica um texto livre (sem persistir nada) usando o pipeline multiagente
    orquestrado via LangGraph (Scribe -> Observer -> Rule Quality -> Inquisitor ->
    Decision). Útil para pré-visualizar como a IA classificaria uma fala antes de
    ela ocorrer numa reunião real.
    """
    require_permission(context, "agent_run.view")
    result = analyze_transcript_text(payload.text)
    return TranscriptAnalysisResponse(
        engine=result.get("engine", "sequential_fallback"),
        normalized_text=result.get("normalized_text", ""),
        is_rule_candidate=result.get("is_rule_candidate", False),
        quality_details=result.get("quality_details", {}),
        is_question_candidate=result.get("is_question_candidate", False),
        is_decision_candidate=result.get("is_decision_candidate", False),
    )


@router.get("/meetings/{meeting_id}/agent-runs", response_model=list[AgentRunResponse])
def list_agent_runs(
    meeting_id: str,
    context: RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    require_permission(context, "agent_run.view")
    meeting = _get_tenant_meeting(db, context, meeting_id)
    runs = list(
        db.scalars(
            select(AgentRun)
            .where(AgentRun.tenant_id == context.tenant_id, AgentRun.meeting_id == meeting.id)
            .order_by(AgentRun.created_at.desc())
        )
    )
    return [agent_run_to_response(run) for run in runs]
