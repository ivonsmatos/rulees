import asyncio
import base64
import binascii
import json
import logging
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.modules.ai_agents.llm_classifier import classify_transcript_text
from app.modules.ai_agents.service import write_agent_run
from app.modules.auth.models import TenantMember
from app.modules.billing.service import ensure_billing_limit, estimate_llm_cost_usd
from app.modules.decisions.service import create_detected_decision
from app.modules.meetings.lifecycle import complete_meeting_processing
from app.modules.meetings.models import Meeting, TranscriptChunk
from app.modules.permissions.service import can_role
from app.modules.questions.service import create_open_question
from app.modules.rag.service import check_rule_conflicts, upsert_embedding
from app.modules.rules_ledger.service import (
    create_candidate_rule,
    create_rule_version,
    normalize_text,
)
from app.modules.transcription.service import TranscriptionResult, TranscriptionSegment, transcribe_audio_bytes
from app.modules.usage.service import write_usage_event
from app.shared.enums import MeetingStatus

router = APIRouter()

logger = logging.getLogger(__name__)

MAX_AUDIO_CHUNK_BYTES = 1_500_000


def _source_reference(chunk: TranscriptChunk) -> dict[str, Any]:
    return {
        "source_type": "transcript_chunk",
        "source_id": chunk.id,
        "start_time": chunk.start_time,
        "end_time": chunk.end_time,
        "quoted_text": chunk.normalized_text,
    }


async def _send_error(
    websocket: WebSocket, code: str, message: str, event_id: str | None = None
) -> None:
    await websocket.send_json(
        {
            "event_id": event_id,
            "event_type": "error.validation",
            "payload": {"code": code, "message": message},
        }
    )


def _number_or_none(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _segment_to_dict(segment: TranscriptionSegment) -> dict[str, Any]:
    return {
        "raw_text": segment.raw_text,
        "start_time": segment.start_time,
        "end_time": segment.end_time,
        "speaker_label": segment.speaker_label,
        "confidence_score": segment.confidence_score,
    }


async def _extract_audio_chunk_payload(event_payload: dict[str, Any]) -> tuple[TranscriptionResult, str, dict[str, Any]]:
    is_final = event_payload.get("is_final")
    final = is_final if isinstance(is_final, bool) else True
    sequence = event_payload.get("sequence")
    sequence_number = sequence if isinstance(sequence, int) else None
    start_time = _number_or_none(event_payload.get("start_time"))
    end_time = _number_or_none(event_payload.get("end_time"))
    speaker_label = event_payload.get("speaker_label") if isinstance(event_payload.get("speaker_label"), str) else None
    language = event_payload.get("language") if isinstance(event_payload.get("language"), str) else "pt-BR"

    text = event_payload.get("text")
    if isinstance(text, str) and text.strip():
        result = TranscriptionResult(
            raw_text=text.strip(),
            provider="manual_text",
            is_final=final,
            language=language,
            start_time=start_time,
            end_time=end_time,
            speaker_label=speaker_label,
            segments=[
                TranscriptionSegment(
                    raw_text=text.strip(),
                    start_time=start_time,
                    end_time=end_time,
                    speaker_label=speaker_label,
                )
            ],
            metadata={"input": "text"},
        )
        return result, "websocket_demo", {"input": "text", "sequence": sequence}

    audio_base64 = event_payload.get("audio_base64")
    if not isinstance(audio_base64, str) or not audio_base64.strip():
        raise ValueError("text or audio_base64 is required")

    clean_audio = audio_base64.strip()
    if clean_audio.startswith("data:") and "," in clean_audio:
        clean_audio = clean_audio.split(",", 1)[1]

    try:
        audio_bytes = base64.b64decode(clean_audio, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid audio_base64 payload") from exc

    if not audio_bytes:
        raise ValueError("Empty audio chunk")
    if len(audio_bytes) > MAX_AUDIO_CHUNK_BYTES:
        raise ValueError("Audio chunk exceeds the accepted size")

    mime_type = str(event_payload.get("mime_type") or "audio/webm")
    if not mime_type.startswith("audio/"):
        raise ValueError("mime_type must be an audio type")

    transcription = await transcribe_audio_bytes(
        audio_bytes,
        mime_type=mime_type,
        sequence=sequence_number,
    )
    if not final or start_time is not None or end_time is not None:
        transcription = replace(
            transcription,
            is_final=final,
            start_time=transcription.start_time if start_time is None else start_time,
            end_time=transcription.end_time if end_time is None else end_time,
        )
    return (
        transcription,
        f"stt_{transcription.provider}",
        {
            "input": "audio",
            "mime_type": mime_type,
            "byte_size": len(audio_bytes),
            "sequence": sequence,
            "stt_provider": transcription.provider,
            "stt_confidence_score": transcription.confidence_score,
            "stt_duration_seconds": transcription.duration_seconds,
            "stt_metadata": transcription.metadata,
            "stt_segments": [_segment_to_dict(segment) for segment in transcription.segments],
        },
    )


@router.websocket("/ws/meetings/{meeting_id}")
async def meeting_socket(websocket: WebSocket, meeting_id: str, token: str) -> None:
    try:
        payload = decode_access_token(token)
    except ValueError:
        await websocket.close(code=4401)
        return

    user_id = payload.get("sub")
    with SessionLocal() as db:
        meeting = db.get(Meeting, meeting_id)
        if meeting is None:
            await websocket.close(code=4404)
            return
        membership = (
            db.query(TenantMember)
            .filter(TenantMember.tenant_id == meeting.tenant_id, TenantMember.user_id == user_id)
            .first()
        )
        if membership is None:
            await websocket.close(code=4403)
            return

    await websocket.accept()
    await websocket.send_json({"event_type": "client.connected", "payload": {"meeting_id": meeting_id}})

    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                await _send_error(websocket, "INVALID_EVENT", "WebSocket event must be an object")
                continue

            event_id = str(message.get("event_id") or "") or None
            event_type = message.get("event_type")
            payload_value = message.get("payload") or {}
            event_payload = payload_value if isinstance(payload_value, dict) else {}

            with SessionLocal() as db:
                try:
                    meeting = db.get(Meeting, meeting_id)
                    if meeting is None:
                        await _send_error(websocket, "MEETING_NOT_FOUND", "Meeting not found", event_id)
                        continue

                    if event_type == "system.ping":
                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "system.pong",
                                "payload": {
                                    "meeting_id": meeting.id,
                                    "server_time": datetime.now(timezone.utc).isoformat(),
                                },
                            }
                        )
                        continue

                    if event_type in {"client.join_meeting", "client.resume_connection"}:
                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "client.connection_ready",
                                "payload": {
                                    "meeting_id": meeting.id,
                                    "status": meeting.status,
                                    "resumed": event_type == "client.resume_connection",
                                },
                            }
                        )
                        continue

                    if event_type == "audio.chunk":
                        membership = (
                            db.query(TenantMember)
                            .filter(TenantMember.tenant_id == meeting.tenant_id, TenantMember.user_id == user_id)
                            .first()
                        )
                        if membership is None or not can_role(membership.role, "audio.chunk.create"):
                            await _send_error(
                                websocket, "FORBIDDEN", "User cannot send audio chunks", event_id
                            )
                            continue
                        if meeting.status != MeetingStatus.active:
                            await _send_error(
                                websocket,
                                "MEETING_NOT_ACTIVE",
                                "Only active meetings receive audio",
                                event_id,
                            )
                            continue
                        try:
                            ensure_billing_limit(
                                db,
                                tenant_id=meeting.tenant_id,
                                event_type="audio_chunk_received",
                            )
                        except HTTPException as exc:
                            await _send_error(
                                websocket,
                                "BILLING_LIMIT_REACHED",
                                str(exc.detail),
                                event_id,
                            )
                            continue

                        try:
                            transcription, source, usage_details = await _extract_audio_chunk_payload(
                                event_payload
                            )
                        except ValueError as exc:
                            await _send_error(websocket, "INVALID_AUDIO_CHUNK", str(exc), event_id)
                            continue

                        normalized = normalize_text(transcription.raw_text)
                        chunk = TranscriptChunk(
                            tenant_id=meeting.tenant_id,
                            project_id=meeting.project_id,
                            meeting_id=meeting.id,
                            raw_text=transcription.raw_text,
                            normalized_text=normalized,
                            is_final=transcription.is_final,
                            start_time=transcription.start_time,
                            end_time=transcription.end_time,
                            speaker_label=transcription.speaker_label,
                            language=transcription.language,
                            confidence_score=transcription.confidence_score,
                            sequence=usage_details.get("sequence")
                            if isinstance(usage_details.get("sequence"), int)
                            else None,
                            source=source,
                            provider_metadata=json.dumps(
                                {
                                    "provider": transcription.provider,
                                    "duration_seconds": transcription.duration_seconds,
                                    "segments": usage_details.get("stt_segments", []),
                                    "metadata": transcription.metadata,
                                }
                            ),
                        )
                        db.add(chunk)
                        db.flush()
                        write_usage_event(
                            db,
                            tenant_id=meeting.tenant_id,
                            project_id=meeting.project_id,
                            meeting_id=meeting.id,
                            user_id=user_id,
                            event_type="audio_chunk_received",
                            unit="chunk",
                            quantity=1,
                            details=usage_details,
                        )
                        scribe_run = write_agent_run(
                            db,
                            tenant_id=meeting.tenant_id,
                            project_id=meeting.project_id,
                            meeting_id=meeting.id,
                            agent_name="Scribe",
                            agent_role="transcript_normalizer",
                            input_reference={
                                "source_type": "websocket_event",
                                "source_ids": [event_id] if event_id else [],
                                "payload_type": usage_details.get("input"),
                            },
                            output={
                                "chunk_id": chunk.id,
                                "raw_text": chunk.raw_text,
                                "normalized_text": chunk.normalized_text,
                                "language": chunk.language or "pt-BR",
                                "speaker_label": chunk.speaker_label,
                                "start_time": chunk.start_time,
                                "end_time": chunk.end_time,
                                "is_final": chunk.is_final,
                                "corrections": [],
                                "semantic_segments": usage_details.get("stt_segments", []),
                            },
                            confidence_score=usage_details.get("stt_confidence_score"),
                            metadata={
                                "source": source,
                                "stt_provider": usage_details.get("stt_provider"),
                                "stt_metadata": usage_details.get("stt_metadata"),
                            },
                        )

                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "transcript.final" if chunk.is_final else "transcript.partial",
                                "payload": {
                                    "id": chunk.id,
                                    "chunk_id": chunk.id,
                                    "meeting_id": meeting.id,
                                    "raw_text": chunk.raw_text,
                                    "normalized_text": chunk.normalized_text,
                                    "is_final": chunk.is_final,
                                    "start_time": chunk.start_time,
                                    "end_time": chunk.end_time,
                                    "speaker_label": chunk.speaker_label,
                                    "language": chunk.language,
                                    "confidence_score": chunk.confidence_score,
                                    "sequence": chunk.sequence,
                                    "source": chunk.source,
                                    "agent_run_id": scribe_run.run_id,
                                },
                            }
                        )

                        if not chunk.is_final:
                            db.commit()
                            await websocket.send_json(
                                {
                                    "event_id": event_id,
                                    "event_type": "system.ack",
                                    "payload": {"event_type": event_type, "user_id": user_id},
                                }
                            )
                            continue

                        classification = await classify_transcript_text(normalized)

                        if classification.usage:
                            estimated_cost = estimate_llm_cost_usd(
                                classification.model_name,
                                prompt_tokens=classification.usage["prompt_tokens"],
                                total_tokens=classification.usage["total_tokens"],
                            )
                            write_usage_event(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                user_id=user_id,
                                event_type="llm_tokens_used",
                                unit="tokens",
                                quantity=classification.usage["total_tokens"],
                                details={
                                    "model": classification.model_name,
                                    "engine": classification.engine,
                                    "prompt_tokens": classification.usage["prompt_tokens"],
                                    "completion_tokens": classification.usage["completion_tokens"],
                                    "estimated_cost_usd": estimated_cost,
                                },
                            )

                        if classification.is_rule_candidate:
                            rule = create_candidate_rule(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                rule_text=normalized,
                                source_chunk_id=chunk.id,
                                condition_text=classification.rule_condition_text,
                                result_text=classification.rule_result_text,
                                confidence_score=classification.rule_confidence,
                            )
                            db.flush()
                            # check_rule_conflicts / upsert_embedding podem chamar providers de
                            # embeddings (OpenAI/Ollama) via httpx sincrono; deslocamos para uma
                            # thread para nao bloquear o event loop do WebSocket (mesmo padrao de
                            # `ai_agents/llm_classifier.py`). Chamadas sequenciais na mesma `db`
                            # Session, nunca em paralelo -- seguro para uso nao-concorrente.
                            guardian_result = await asyncio.to_thread(
                                check_rule_conflicts,
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                rule_id=rule.id,
                                rule_text=rule.rule_text,
                            )
                            rule.status = guardian_result.recommended_status
                            await asyncio.to_thread(
                                upsert_embedding,
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                source_type="business_rule",
                                source_id=rule.id,
                                content=rule.rule_text,
                            )
                            create_rule_version(
                                db,
                                rule,
                                created_by=user_id,
                                change_reason="Regra candidata detectada pela IA",
                            )
                            write_usage_event(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                user_id=user_id,
                                event_type="ai_rule_detected",
                                details={"rule_id": rule.id, "rule_code": rule.code},
                            )
                            write_usage_event(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                user_id=user_id,
                                event_type="rag_conflict_checked",
                                details={
                                    "rule_id": rule.id,
                                    "result_type": guardian_result.result_type,
                                    "requires_human_resolution": guardian_result.requires_human_resolution,
                                },
                            )
                            observer_run = write_agent_run(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                agent_name="Observer",
                                agent_role="business_rule_extractor",
                                input_reference={
                                    "source_type": "transcript_chunk",
                                    "source_ids": [chunk.id],
                                },
                                output={
                                    "detected_items": [
                                        {
                                            "item_type": "business_rule",
                                            "rule_candidate": {
                                                "id": rule.id,
                                                "code": rule.code,
                                                "rule_text": rule.rule_text,
                                                "status_recommendation": rule.status,
                                                "confidence_score": rule.confidence_score,
                                                "quality_score": rule.quality_score,
                                                "source_references": [_source_reference(chunk)],
                                            },
                                        }
                                    ],
                                    "risks": [],
                                    "dependencies": [],
                                },
                                confidence_score=rule.confidence_score,
                                model_name=classification.model_name,
                                prompt_version=classification.prompt_version,
                                warnings=classification.warnings,
                                metadata={"execution_mode": classification.engine},
                            )
                            rag_guardian_run = write_agent_run(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                agent_name="RAG Guardian",
                                agent_role="historical_consistency_checker",
                                input_reference={
                                    "source_type": "business_rule",
                                    "source_ids": [rule.id],
                                },
                                output={
                                    "history_verified": guardian_result.history_verified,
                                    "result_type": guardian_result.result_type,
                                    "requires_human_resolution": guardian_result.requires_human_resolution,
                                    "summary": guardian_result.summary,
                                    "retrieved_sources": guardian_result.retrieved_sources,
                                    "conflicts": guardian_result.conflicts,
                                    "recommended_status": guardian_result.recommended_status,
                                },
                                confidence_score=1.0,
                                metadata={"retriever": "tenant_project_hash_cosine"},
                            )
                            quality_details = json.loads(rule.quality_details) if rule.quality_details else {}
                            quality_run = write_agent_run(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
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
                                metadata={"scoring_method": "deterministic_checklist_v1"},
                            )
                            await websocket.send_json(
                                {
                                    "event_id": event_id,
                                    "event_type": "ai.rule.detected",
                                    "payload": {
                                        "id": rule.id,
                                        "code": rule.code,
                                        "rule_text": rule.rule_text,
                                        "status": rule.status,
                                        "version_number": rule.version_number,
                                        "confidence_score": rule.confidence_score,
                                        "quality_score": rule.quality_score,
                                        "source_chunk_ids": [chunk.id],
                                        "agent_run_id": observer_run.run_id,
                                        "rag_guardian_run_id": rag_guardian_run.run_id,
                                        "quality_run_id": quality_run.run_id,
                                        "rag_result_type": guardian_result.result_type,
                                        "requires_human_resolution": guardian_result.requires_human_resolution,
                                    },
                                }
                            )

                        if classification.is_question_candidate:
                            question = create_open_question(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                text=normalized,
                                source_chunk_id=chunk.id,
                                question_text=classification.question_text,
                                reason=classification.question_reason,
                                gap_type=classification.question_gap_type,
                                priority=classification.question_priority,
                                confidence_score=classification.question_confidence,
                            )
                            db.flush()
                            write_usage_event(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                user_id=user_id,
                                event_type="ai_question_suggested",
                                details={"question_id": question.id},
                            )
                            inquisitor_run = write_agent_run(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                agent_name="Inquisitor",
                                agent_role="gap_detector",
                                input_reference={
                                    "source_type": "transcript_chunk",
                                    "source_ids": [chunk.id],
                                },
                                output={
                                    "questions": [
                                        {
                                            "id": question.id,
                                            "question_text": question.question_text,
                                            "reason": question.reason,
                                            "gap_type": question.gap_type,
                                            "priority": question.priority,
                                            "related_rule_id": None,
                                            "expected_answer_type": "free_text",
                                            "source_references": [_source_reference(chunk)],
                                        }
                                    ]
                                },
                                confidence_score=question.confidence_score,
                                model_name=classification.model_name,
                                prompt_version=classification.prompt_version,
                                warnings=classification.warnings,
                                metadata={"execution_mode": classification.engine},
                            )
                            await websocket.send_json(
                                {
                                    "event_id": event_id,
                                    "event_type": "ai.question.suggested",
                                    "payload": {
                                        "id": question.id,
                                        "question_text": question.question_text,
                                        "reason": question.reason,
                                        "gap_type": question.gap_type,
                                        "priority": question.priority,
                                        "status": question.status,
                                        "confidence_score": question.confidence_score,
                                        "source_chunk_ids": [chunk.id],
                                        "agent_run_id": inquisitor_run.run_id,
                                    },
                                }
                            )

                        if classification.is_decision_candidate:
                            decision = create_detected_decision(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                text=normalized,
                                source_chunk_id=chunk.id,
                                decision_type=classification.decision_type,
                                confidence_score=classification.decision_confidence,
                            )
                            db.flush()
                            write_usage_event(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                user_id=user_id,
                                event_type="ai_decision_detected",
                                details={"decision_id": decision.id},
                            )
                            decision_run = write_agent_run(
                                db,
                                tenant_id=meeting.tenant_id,
                                project_id=meeting.project_id,
                                meeting_id=meeting.id,
                                agent_name="Decision",
                                agent_role="decision_detector",
                                input_reference={
                                    "source_type": "transcript_chunk",
                                    "source_ids": [chunk.id],
                                },
                                output={
                                    "decisions": [
                                        {
                                            "id": decision.id,
                                            "decision_text": decision.decision_text,
                                            "decision_type": decision.decision_type,
                                            "status": decision.status,
                                            "responsible_area": decision.responsible_area,
                                            "source_references": [_source_reference(chunk)],
                                        }
                                    ]
                                },
                                confidence_score=decision.confidence_score,
                                model_name=classification.model_name,
                                prompt_version=classification.prompt_version,
                                warnings=classification.warnings,
                                metadata={"execution_mode": classification.engine},
                            )
                            await websocket.send_json(
                                {
                                    "event_id": event_id,
                                    "event_type": "ai.decision.detected",
                                    "payload": {
                                        "id": decision.id,
                                        "decision_text": decision.decision_text,
                                        "decision_type": decision.decision_type,
                                        "status": decision.status,
                                        "responsible_area": decision.responsible_area,
                                        "confidence_score": decision.confidence_score,
                                        "source_chunk_ids": [chunk.id],
                                        "agent_run_id": decision_run.run_id,
                                    },
                                }
                            )

                        db.commit()
                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "system.ack",
                                "payload": {"event_type": event_type, "user_id": user_id},
                            }
                        )
                        continue

                    if event_type == "meeting.stop":
                        meeting.status = MeetingStatus.processing
                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "meeting.processing",
                                "payload": {"meeting_id": meeting.id, "status": meeting.status},
                            }
                        )
                        # Consolida a reuniao (contagem de regras/duvidas/decisoes) e
                        # transiciona processing -> processing_completed; sem isso a
                        # reuniao ficava presa em `processing` para sempre na UI.
                        meeting, processing_summary = complete_meeting_processing(db, meeting)
                        db.commit()
                        if meeting.status == MeetingStatus.processing_completed:
                            await websocket.send_json(
                                {
                                    "event_id": event_id,
                                    "event_type": "meeting.processing_completed",
                                    "payload": {
                                        "meeting_id": meeting.id,
                                        "status": meeting.status,
                                        "rules_count": processing_summary.rules_count,
                                        "questions_count": processing_summary.questions_count,
                                        "decisions_count": processing_summary.decisions_count,
                                    },
                                }
                            )
                        continue

                    await websocket.send_json(
                        {
                            "event_id": event_id,
                            "event_type": "system.nack",
                            "payload": {"event_type": event_type, "reason": "Unsupported event"},
                        }
                    )
                except WebSocketDisconnect:
                    raise
                except Exception:
                    db.rollback()
                    logger.exception(
                        "Erro inesperado ao processar evento WebSocket (event_type=%s, event_id=%s)",
                        event_type,
                        event_id,
                    )
                    try:
                        await websocket.send_json(
                            {
                                "event_id": event_id,
                                "event_type": "error.validation",
                                "payload": {
                                    "code": "INTERNAL_ERROR",
                                    "message": "Erro interno ao processar o evento. Tente novamente.",
                                },
                            }
                        )
                    except Exception:
                        logger.exception("Falha ao notificar cliente sobre erro interno.")
                    continue
    except WebSocketDisconnect:
        return
