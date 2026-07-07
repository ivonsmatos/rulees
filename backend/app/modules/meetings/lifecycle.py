from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict
from app.modules.decisions.models import Decision
from app.modules.meetings.models import ConsentRecord, Meeting, MeetingParticipant
from app.modules.questions.models import OpenQuestion
from app.modules.rules_ledger.models import BusinessRule
from app.shared.enums import MeetingStatus


def assert_meeting_can_start(db: Session, meeting: Meeting) -> None:
    if meeting.status not in {MeetingStatus.scheduled, MeetingStatus.ready, MeetingStatus.paused}:
        raise conflict(f"Meeting cannot start from status {meeting.status}")
    required_participants = list(
        db.scalars(
            select(MeetingParticipant).where(
                MeetingParticipant.meeting_id == meeting.id,
                MeetingParticipant.consent_required.is_(True),
            )
        )
    )
    if required_participants:
        for participant in required_participants:
            consent_exists = db.scalar(
                select(ConsentRecord.id).where(
                    ConsentRecord.meeting_id == meeting.id,
                    ConsentRecord.user_id == participant.user_id,
                    ConsentRecord.revoked_at.is_(None),
                )
            )
            if consent_exists is None:
                raise bad_request("Active consent is required for every required participant")
        return
    consent_exists = db.scalar(
        select(ConsentRecord.id).where(
            ConsentRecord.meeting_id == meeting.id,
            ConsentRecord.revoked_at.is_(None),
        )
    )
    if consent_exists is None:
        raise bad_request("Consent is required before starting the meeting")


def start_meeting(db: Session, meeting: Meeting) -> Meeting:
    assert_meeting_can_start(db, meeting)
    meeting.status = MeetingStatus.active
    if meeting.started_at is None:
        meeting.started_at = datetime.now(timezone.utc)
    return meeting


def pause_meeting(meeting: Meeting) -> Meeting:
    if meeting.status != MeetingStatus.active:
        raise conflict("Only active meetings can be paused")
    meeting.status = MeetingStatus.paused
    return meeting


def resume_meeting(db: Session, meeting: Meeting) -> Meeting:
    assert_meeting_can_start(db, meeting)
    meeting.status = MeetingStatus.active
    return meeting


def finish_meeting(meeting: Meeting) -> Meeting:
    if meeting.status not in {MeetingStatus.active, MeetingStatus.paused}:
        raise conflict("Only active or paused meetings can be finished")
    meeting.status = MeetingStatus.processing
    meeting.ended_at = datetime.now(timezone.utc)
    return meeting


@dataclass
class MeetingProcessingSummary:
    """Fechamento simples da reuniao (Etapa 19 -- "Processamento final" do fluxo)."""

    rules_count: int
    questions_count: int
    decisions_count: int

    def to_dict(self) -> dict[str, int]:
        return {
            "rules_count": self.rules_count,
            "questions_count": self.questions_count,
            "decisions_count": self.decisions_count,
        }


def complete_meeting_processing(db: Session, meeting: Meeting) -> tuple[Meeting, MeetingProcessingSummary]:
    """Consolida a reuniao e transiciona `processing` -> `processing_completed`.

    Sem essa chamada a reuniao ficava presa para sempre em `processing` na UI
    apos ser finalizada -- nada no codigo fazia essa transicao.

    Estado-alvo confirmado em `documentos/Fluxo Completo da Reuniao.docx`
    (secao 5, "Transicoes permitidas de estado"): `processing -> processing_completed`.
    `processing_completed -> finished` e uma transicao posterior (ligada a
    revisao/aprovacao humana do documento -- fora do escopo desta correcao).

    Idempotente: se a reuniao ja saiu de `processing`, apenas retorna o estado
    atual sem recalcular nem sobrescrever o status.
    """
    rules_count = (
        db.scalar(
            select(func.count()).select_from(BusinessRule).where(
                BusinessRule.tenant_id == meeting.tenant_id,
                BusinessRule.meeting_id == meeting.id,
            )
        )
        or 0
    )
    questions_count = (
        db.scalar(
            select(func.count()).select_from(OpenQuestion).where(
                OpenQuestion.tenant_id == meeting.tenant_id,
                OpenQuestion.meeting_id == meeting.id,
            )
        )
        or 0
    )
    decisions_count = (
        db.scalar(
            select(func.count()).select_from(Decision).where(
                Decision.tenant_id == meeting.tenant_id,
                Decision.meeting_id == meeting.id,
            )
        )
        or 0
    )
    summary = MeetingProcessingSummary(
        rules_count=rules_count,
        questions_count=questions_count,
        decisions_count=decisions_count,
    )
    if meeting.status == MeetingStatus.processing:
        meeting.status = MeetingStatus.processing_completed
    return meeting, summary
