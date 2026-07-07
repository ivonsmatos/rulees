from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict
from app.modules.meetings.models import ConsentRecord, Meeting, MeetingParticipant
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
