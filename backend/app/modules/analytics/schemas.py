from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    projects_total: int
    meetings_total: int
    rules_total: int
    approved_rules: int
    documents_total: int
    open_questions: int
    comments_total: int
    notifications_unread: int
    readiness_score: int
