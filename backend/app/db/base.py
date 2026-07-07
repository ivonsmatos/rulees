from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.modules.auth.models import Tenant, TenantInvite, TenantMember, User  # noqa: E402,F401
from app.modules.ai_agents.models import AgentRun  # noqa: E402,F401
from app.modules.audit.models import AuditLog  # noqa: E402,F401
from app.modules.comments.models import Comment  # noqa: E402,F401
from app.modules.decisions.models import Decision  # noqa: E402,F401
from app.modules.documents.models import Document, DocumentExportJob, DocumentSection, DocumentVersion  # noqa: E402,F401
from app.modules.feedback.models import BetaFeedback  # noqa: E402,F401
from app.modules.billing.models import TenantBillingProfile  # noqa: E402,F401
from app.modules.meetings.models import ConsentRecord, Meeting, MeetingLifecycleEvent, MeetingParticipant, TranscriptChunk  # noqa: E402,F401
from app.modules.projects.models import Project, ProjectGlossaryTerm, ProjectMember, ProjectTemplate  # noqa: E402,F401
from app.modules.questions.models import OpenQuestion  # noqa: E402,F401
from app.modules.notifications.models import Notification  # noqa: E402,F401
from app.modules.rag.models import SemanticEmbedding  # noqa: E402,F401
from app.modules.rules_ledger.models import BusinessRule, RuleLifecycleEvent, RuleVersion  # noqa: E402,F401
from app.modules.usage.models import UsageEvent  # noqa: E402,F401
