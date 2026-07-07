from enum import StrEnum


class TenantRole(StrEnum):
    admin = "admin"
    manager = "manager"
    member = "member"
    viewer = "viewer"


class ProjectStatus(StrEnum):
    active = "active"
    archived = "archived"


class MeetingStatus(StrEnum):
    scheduled = "scheduled"
    ready = "ready"
    active = "active"
    paused = "paused"
    processing = "processing"
    processing_completed = "processing_completed"
    finished = "finished"
    cancelled = "cancelled"
    failed = "failed"


class RuleStatus(StrEnum):
    draft = "draft"
    needs_review = "needs_review"
    in_validation = "in_validation"
    conflict_detected = "conflict_detected"
    approved = "approved"
    approved_incomplete_for_dev = "approved_incomplete_for_dev"
    rejected = "rejected"
    replaced = "replaced"
    revoked = "revoked"
    archived = "archived"


class DocumentStatus(StrEnum):
    not_generated = "not_generated"
    generating = "generating"
    draft = "draft"
    ready = "ready"
    approved = "approved"
    rejected = "rejected"
    exported = "exported"
    archived = "archived"
    failed = "failed"


class AgentRunStatus(StrEnum):
    success = "success"
    partial_success = "partial_success"
    no_relevant_content = "no_relevant_content"
    failed = "failed"
    skipped = "skipped"
