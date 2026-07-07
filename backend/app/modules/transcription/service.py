from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.settings import get_settings


@dataclass(frozen=True)
class TranscriptionSegment:
    raw_text: str
    start_time: float | None = None
    end_time: float | None = None
    speaker_label: str | None = None
    confidence_score: float | None = None


@dataclass(frozen=True)
class TranscriptionResult:
    raw_text: str
    provider: str
    is_final: bool = True
    language: str = "pt-BR"
    start_time: float | None = None
    end_time: float | None = None
    speaker_label: str | None = None
    confidence_score: float | None = None
    duration_seconds: float | None = None
    segments: list[TranscriptionSegment] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _mock_transcription(byte_size: int, sequence: int | None) -> TranscriptionResult:
    sequence_text = f" chunk {sequence}" if sequence is not None else ""
    start_time = float(max((sequence or 1) - 1, 0) * 2.5)
    end_time = start_time + 2.5
    raw_text = f"Trecho de audio{sequence_text} recebido ({byte_size} bytes) aguardando STT real."
    return TranscriptionResult(
        raw_text=raw_text,
        provider="mock",
        start_time=start_time,
        end_time=end_time,
        duration_seconds=2.5,
        segments=[
            TranscriptionSegment(
                raw_text=raw_text,
                start_time=start_time,
                end_time=end_time,
                speaker_label="speaker_0",
            )
        ],
        metadata={"fallback": True, "diarization": "mock"},
    )


def _speaker_label(value: Any) -> str | None:
    if value is None:
        return None
    return f"speaker_{value}"


def _deepgram_segments(payload: dict[str, Any]) -> list[TranscriptionSegment]:
    utterances = payload.get("results", {}).get("utterances", [])
    segments: list[TranscriptionSegment] = []
    if isinstance(utterances, list):
        for utterance in utterances:
            transcript = str(utterance.get("transcript") or "").strip()
            if not transcript:
                continue
            segments.append(
                TranscriptionSegment(
                    raw_text=transcript,
                    start_time=utterance.get("start") if isinstance(utterance.get("start"), int | float) else None,
                    end_time=utterance.get("end") if isinstance(utterance.get("end"), int | float) else None,
                    speaker_label=_speaker_label(utterance.get("speaker")),
                    confidence_score=utterance.get("confidence")
                    if isinstance(utterance.get("confidence"), int | float)
                    else None,
                )
            )
    if segments:
        return segments

    channels = payload.get("results", {}).get("channels", [])
    for channel in channels:
        alternatives = channel.get("alternatives", [])
        for alternative in alternatives:
            transcript = str(alternative.get("transcript") or "").strip()
            words = alternative.get("words", [])
            if isinstance(words, list) and words:
                current_words: list[str] = []
                current_speaker: str | None = None
                start_time: float | None = None
                end_time: float | None = None
                confidences: list[float] = []
                for word in words:
                    speaker = _speaker_label(word.get("speaker"))
                    if current_words and speaker != current_speaker:
                        segments.append(
                            TranscriptionSegment(
                                raw_text=" ".join(current_words),
                                start_time=start_time,
                                end_time=end_time,
                                speaker_label=current_speaker,
                                confidence_score=sum(confidences) / len(confidences) if confidences else None,
                            )
                        )
                        current_words = []
                        start_time = None
                        confidences = []
                    current_speaker = speaker
                    current_words.append(str(word.get("punctuated_word") or word.get("word") or ""))
                    if start_time is None and isinstance(word.get("start"), int | float):
                        start_time = float(word["start"])
                    if isinstance(word.get("end"), int | float):
                        end_time = float(word["end"])
                    if isinstance(word.get("confidence"), int | float):
                        confidences.append(float(word["confidence"]))
                if current_words:
                    segments.append(
                        TranscriptionSegment(
                            raw_text=" ".join(current_words).strip(),
                            start_time=start_time,
                            end_time=end_time,
                            speaker_label=current_speaker,
                            confidence_score=sum(confidences) / len(confidences) if confidences else None,
                        )
                    )
            if transcript and not segments:
                confidence = alternative.get("confidence")
                segments.append(
                    TranscriptionSegment(
                        raw_text=transcript,
                        confidence_score=confidence if isinstance(confidence, float | int) else None,
                    )
                )
            if segments:
                return segments
    return []


async def _transcribe_with_deepgram(audio_bytes: bytes, mime_type: str) -> TranscriptionResult:
    settings = get_settings()
    params = {
        "model": settings.deepgram_model,
        "language": settings.deepgram_language,
        "smart_format": "true",
        "diarize": str(settings.stt_diarize).lower(),
        "utterances": str(settings.stt_diarize).lower(),
    }
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key}",
        "Content-Type": mime_type,
    }

    async with httpx.AsyncClient(timeout=settings.stt_timeout_seconds) as client:
        response = await client.post(
            "https://api.deepgram.com/v1/listen",
            params=params,
            headers=headers,
            content=audio_bytes,
        )
        response.raise_for_status()
        payload = response.json()

    segments = _deepgram_segments(payload)
    transcript = " ".join(segment.raw_text for segment in segments).strip()
    confidence_values = [segment.confidence_score for segment in segments if segment.confidence_score is not None]
    confidence = sum(confidence_values) / len(confidence_values) if confidence_values else None
    duration = payload.get("metadata", {}).get("duration")
    start_values = [segment.start_time for segment in segments if segment.start_time is not None]
    end_values = [segment.end_time for segment in segments if segment.end_time is not None]
    return TranscriptionResult(
        raw_text=transcript or "Audio recebido sem fala detectada pelo STT.",
        provider="deepgram",
        language=settings.deepgram_language,
        start_time=min(start_values) if start_values else None,
        end_time=max(end_values) if end_values else None,
        speaker_label=segments[0].speaker_label if len({segment.speaker_label for segment in segments}) == 1 else None,
        confidence_score=confidence,
        duration_seconds=duration if isinstance(duration, float | int) else None,
        segments=segments,
        metadata={
            "model": settings.deepgram_model,
            "language": settings.deepgram_language,
            "request_id": payload.get("metadata", {}).get("request_id"),
            "diarize": settings.stt_diarize,
        },
    )


async def transcribe_audio_bytes(
    audio_bytes: bytes,
    *,
    mime_type: str,
    sequence: int | None = None,
) -> TranscriptionResult:
    settings = get_settings()
    provider = settings.stt_provider.lower().strip()

    if provider == "deepgram" and settings.deepgram_api_key:
        try:
            return await _transcribe_with_deepgram(audio_bytes, mime_type)
        except httpx.HTTPError as exc:
            result = _mock_transcription(len(audio_bytes), sequence)
            return TranscriptionResult(
                raw_text=result.raw_text,
                provider=result.provider,
                metadata={
                    **result.metadata,
                    "stt_error": exc.__class__.__name__,
                    "requested_provider": "deepgram",
                },
            )

    result = _mock_transcription(len(audio_bytes), sequence)
    if provider == "deepgram" and not settings.deepgram_api_key:
        return TranscriptionResult(
            raw_text=result.raw_text,
            provider=result.provider,
            metadata={**result.metadata, "warning": "missing_deepgram_api_key"},
        )
    return result
