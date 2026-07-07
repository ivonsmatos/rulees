from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.documents.models import Document, DocumentSection, DocumentVersion


def render_document_content(title: str, sections: list[dict]) -> str:
    lines = [f"# {title}", ""]
    for section in sections:
        lines.extend([f"## {section['title']}", section["body"], ""])
    return "\n".join(lines).strip()


def render_markdown_export(document: Document, sections: list[DocumentSection]) -> str:
    if not sections:
        return document.content
    lines = [f"# {document.title}", ""]
    for section in sorted(sections, key=lambda item: item.sort_order):
        lines.extend([f"## {section.title}", section.body.strip(), ""])
    return "\n".join(lines).strip()


def build_jira_payload(document: Document, markdown: str) -> dict:
    return {
        "summary": document.title,
        "description": markdown,
        "labels": ["rulees", "functional-document"],
        "metadata": {
            "document_id": document.id,
            "project_id": document.project_id,
            "meeting_id": document.meeting_id,
        },
    }


def build_confluence_payload(document: Document, markdown: str) -> dict:
    return {
        "title": document.title,
        "body": {
            "representation": "storage",
            "value": markdown.replace("\n", "<br />"),
        },
        "metadata": {
            "properties": {
                "rulees_document_id": document.id,
                "rulees_project_id": document.project_id,
                "rulees_meeting_id": document.meeting_id,
            }
        },
    }


def create_document_sections(
    db: Session,
    *,
    tenant_id: str,
    document_id: str,
    sections: list[dict],
) -> list[DocumentSection]:
    created_sections: list[DocumentSection] = []
    for index, section in enumerate(sections, start=1):
        created = DocumentSection(
            tenant_id=tenant_id,
            document_id=document_id,
            section_key=section["section_key"],
            title=section["title"],
            body=section["body"],
            sort_order=index,
        )
        db.add(created)
        created_sections.append(created)
    return created_sections


def next_document_version_number(db: Session, tenant_id: str, document_id: str) -> int:
    latest = db.scalar(
        select(func.max(DocumentVersion.version_number)).where(
            DocumentVersion.tenant_id == tenant_id,
            DocumentVersion.document_id == document_id,
        )
    )
    return (latest or 0) + 1


def create_document_version(
    db: Session,
    document: Document,
    *,
    created_by: str | None,
    change_reason: str,
) -> DocumentVersion:
    version = DocumentVersion(
        tenant_id=document.tenant_id,
        project_id=document.project_id,
        meeting_id=document.meeting_id,
        document_id=document.id,
        version_number=next_document_version_number(db, document.tenant_id, document.id),
        title=document.title,
        status=document.status,
        content=document.content,
        change_reason=change_reason,
        created_by=created_by,
    )
    db.add(version)
    return version
