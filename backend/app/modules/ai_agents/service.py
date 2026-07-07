import json
import time
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.ai_agents.models import AgentRun
from app.shared.enums import AgentRunStatus

AGENT_OUTPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "transcript_normalizer": {
        "schema_version": "scribe.v1",
        "required": ["chunk_id", "raw_text", "normalized_text", "language"],
    },
    "business_rule_extractor": {
        "schema_version": "observer.v1",
        "required": ["detected_items", "risks", "dependencies"],
    },
    "historical_consistency_checker": {
        "schema_version": "rag_guardian.v1",
        "required": ["history_verified", "result_type", "recommended_status"],
    },
    "gap_detector": {
        "schema_version": "inquisitor.v1",
        "required": ["questions"],
    },
    "decision_detector": {
        "schema_version": "decision.v1",
        "required": ["decisions"],
    },
    "requirements_analyst": {
        "schema_version": "requirements.v1",
        "required": ["requirements", "source_references"],
    },
    "technical_writer": {
        "schema_version": "tech_writer.v1",
        "required": ["document_id", "sections"],
    },
    "traceability_mapper": {
        "schema_version": "traceability.v1",
        "required": ["links"],
    },
    "compliance_checker": {
        "schema_version": "compliance.v1",
        "required": ["checks", "warnings"],
    },
    "rule_quality_scorer": {
        "schema_version": "rule_quality.v1",
        "required": ["score", "checks", "missing", "evidence_count"],
    },
}


def _json_dump(value: Any, fallback: Any) -> str:
    return json.dumps(value if value is not None else fallback, ensure_ascii=False)


def _json_load(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def write_agent_run(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    meeting_id: str,
    agent_name: str,
    agent_role: str,
    status: str = AgentRunStatus.success,
    input_reference: dict[str, Any] | None = None,
    output: dict[str, Any] | None = None,
    confidence_score: float | None = None,
    latency_ms: int | None = None,
    model_name: str | None = "local_heuristic",
    prompt_version: str = "local_v1",
    warnings: list[Any] | None = None,
    errors: list[Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AgentRun:
    output_payload = output or {}
    schema = AGENT_OUTPUT_SCHEMAS.get(agent_role, {"schema_version": "generic.v1", "required": []})
    schema_warnings = list(warnings or [])
    for key in schema["required"]:
        if key not in output_payload:
            schema_warnings.append({"code": "SCHEMA_FIELD_MISSING", "field": key})
    latency_value = latency_ms if latency_ms is not None else max(int((time.perf_counter() % 1) * 1000), 1)
    run = AgentRun(
        run_id=f"run_{agent_role}_{uuid4().hex}",
        tenant_id=tenant_id,
        project_id=project_id,
        meeting_id=meeting_id,
        agent_name=agent_name,
        agent_role=agent_role,
        status=str(status),
        confidence_score=confidence_score,
        latency_ms=latency_value,
        model_name=model_name,
        prompt_version=prompt_version,
        input_reference=_json_dump(input_reference, {}),
        output=_json_dump(output_payload, {}),
        warnings=_json_dump(schema_warnings, []),
        errors=_json_dump(errors, []),
        run_metadata=_json_dump(
            {
                "execution_mode": "local_heuristic",
                **(metadata or {}),
                "output_schema": schema,
            },
            {},
        ),
    )
    db.add(run)
    return run


def agent_run_to_response(run: AgentRun) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "run_id": run.run_id,
        "tenant_id": run.tenant_id,
        "project_id": run.project_id,
        "meeting_id": run.meeting_id,
        "agent_name": run.agent_name,
        "agent_role": run.agent_role,
        "status": run.status,
        "confidence_score": run.confidence_score,
        "input_reference": _json_load(run.input_reference, {}),
        "output": _json_load(run.output, {}),
        "warnings": _json_load(run.warnings, []),
        "errors": _json_load(run.errors, []),
        "metadata": {
            **_json_load(run.run_metadata, {}),
            "model": run.model_name,
            "prompt_version": run.prompt_version,
            "latency_ms": run.latency_ms,
        },
        "created_at": run.created_at,
    }
