from app.modules.transcription.service import _deepgram_segments, _mock_transcription


def test_deepgram_segments_extract_timestamps_and_speakers_from_utterances() -> None:
    payload = {
        "results": {
            "utterances": [
                {
                    "transcript": "Cliente premium precisa de revisao.",
                    "start": 1.2,
                    "end": 3.4,
                    "speaker": 0,
                    "confidence": 0.91,
                },
                {
                    "transcript": "A regra deve ser aprovada.",
                    "start": 3.5,
                    "end": 5.1,
                    "speaker": 1,
                    "confidence": 0.87,
                },
            ]
        }
    }

    segments = _deepgram_segments(payload)

    assert [segment.speaker_label for segment in segments] == ["speaker_0", "speaker_1"]
    assert segments[0].start_time == 1.2
    assert segments[1].end_time == 5.1
    assert segments[0].confidence_score == 0.91


def test_mock_transcription_has_deterministic_timestamps_and_diarization() -> None:
    result = _mock_transcription(byte_size=1200, sequence=3)

    assert result.start_time == 5.0
    assert result.end_time == 7.5
    assert result.duration_seconds == 2.5
    assert result.segments[0].speaker_label == "speaker_0"
