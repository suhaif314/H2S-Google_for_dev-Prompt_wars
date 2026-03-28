"""
Comprehensive tests for TriageAI input validation, sanitization,
output model validation, and edge cases.

Run with: python -m pytest tests/test_input_validation.py -v
"""

import pytest
from backend.utils.validators import (
    sanitize_text,
    validate_audio_file,
    validate_document_file,
    extract_location_hints,
)


# ── Text Sanitization ───────────────────────────────────────────

class TestSanitizeText:
    """Verify sanitization removes dangerous content but keeps emergency info."""

    def test_strips_whitespace(self):
        assert sanitize_text("  hello world  ") == "hello world"

    def test_removes_null_bytes(self):
        assert sanitize_text("hello\x00world") == "helloworld"

    def test_collapses_excessive_whitespace(self):
        assert sanitize_text("hello    world") == "hello world"

    def test_empty_string(self):
        assert sanitize_text("") == ""

    def test_none_input(self):
        assert sanitize_text(None) == ""

    def test_truncation_at_5000(self):
        long_text = "a" * 6000
        result = sanitize_text(long_text)
        assert len(result) == 5000

    def test_preserves_newlines(self):
        text = "line1\nline2\nline3"
        assert "\n" in sanitize_text(text)

    def test_collapses_excessive_newlines(self):
        text = "line1\n\n\n\n\nline2"
        result = sanitize_text(text)
        assert "\n\n\n" not in result

    def test_preserves_emergency_details(self):
        text = "Fire at 123 Main St. — 5 victims, ages: 45 & 67"
        result = sanitize_text(text)
        assert "123 Main St" in result
        assert "5 victims" in result

    def test_long_input_no_crash(self):
        """Extremely long input should not raise."""
        result = sanitize_text("Emergency! " * 2000)
        assert len(result) > 0


# ── Audio File Validation ────────────────────────────────────────

class TestValidateAudioFile:
    """Verify audio file type and size validation."""

    def test_valid_webm(self):
        is_valid, error = validate_audio_file("audio/webm", 1024)
        assert is_valid is True
        assert error == ""

    def test_valid_wav(self):
        is_valid, _ = validate_audio_file("audio/wav", 1024)
        assert is_valid is True

    def test_valid_mp3(self):
        is_valid, _ = validate_audio_file("audio/mpeg", 1024)
        assert is_valid is True

    def test_valid_ogg(self):
        is_valid, _ = validate_audio_file("audio/ogg", 1024)
        assert is_valid is True

    def test_invalid_type(self):
        is_valid, error = validate_audio_file("video/mp4", 1024)
        assert is_valid is False
        assert "Unsupported" in error

    def test_image_rejected(self):
        is_valid, error = validate_audio_file("image/png", 1024)
        assert is_valid is False

    def test_too_large(self):
        is_valid, error = validate_audio_file("audio/webm", 20 * 1024 * 1024)
        assert is_valid is False
        assert "too large" in error

    def test_empty_file(self):
        is_valid, error = validate_audio_file("audio/webm", 0)
        assert is_valid is False
        assert "empty" in error

    def test_no_content_type(self):
        is_valid, _ = validate_audio_file(None, 1024)
        assert is_valid is False


# ── Document File Validation ─────────────────────────────────────

class TestValidateDocumentFile:
    """Verify document file type and size validation."""

    def test_valid_pdf(self):
        is_valid, _ = validate_document_file("application/pdf", 1024)
        assert is_valid is True

    def test_invalid_type(self):
        is_valid, error = validate_document_file("text/plain", 1024)
        assert is_valid is False
        assert "Unsupported" in error

    def test_word_doc_rejected(self):
        is_valid, _ = validate_document_file("application/msword", 1024)
        assert is_valid is False

    def test_too_large(self):
        is_valid, _ = validate_document_file("application/pdf", 20 * 1024 * 1024)
        assert is_valid is False

    def test_empty(self):
        is_valid, _ = validate_document_file("application/pdf", 0)
        assert is_valid is False

    def test_no_content_type(self):
        is_valid, _ = validate_document_file(None, 1024)
        assert is_valid is False


# ── Location Extraction ──────────────────────────────────────────

class TestExtractLocationHints:
    """Verify regex-based location extraction from free text."""

    def test_extracts_street_address(self):
        text = "There's an accident at 123 Main Street"
        result = extract_location_hints(text)
        assert result is not None
        assert "Main Street" in result

    def test_extracts_near_highway(self):
        text = "Crash near the I-95 highway"
        result = extract_location_hints(text)
        # May or may not match — should not crash
        assert result is None or isinstance(result, str)

    def test_no_location_text(self):
        result = extract_location_hints("Someone needs help urgently")
        assert result is None or isinstance(result, str)

    def test_empty_input(self):
        assert extract_location_hints("") is None
        assert extract_location_hints(None) is None

    def test_extracts_avenue(self):
        text = "Fire at 456 Oak Avenue"
        result = extract_location_hints(text)
        assert result is not None
        assert "Oak Avenue" in result


# ── Pydantic Output Models ───────────────────────────────────────

class TestOutputModels:
    """Verify Pydantic model validation for AI output parsing."""

    def test_triage_report_creation(self):
        from backend.models.output_models import TriageReport
        report = TriageReport(
            incident_id="test-123",
            timestamp="2026-03-28T12:00:00Z",
            incident_type="FIRE",
            severity={"score": 4, "justification": "Active fire with trapped victims"},
            summary="Building fire with trapped occupants",
            extracted_details={
                "location": "123 Main St",
                "num_affected": "5",
                "injuries_described": ["burns", "smoke inhalation"],
                "hazards_present": ["active fire", "structural collapse"],
                "caller_emotional_state": "panicked",
            },
            immediate_actions=[
                {"priority": 1, "action": "Dispatch fire trucks", "responsible_party": "Fire Dept"},
            ],
            resources_needed={"ambulances": 3, "fire_trucks": 4, "police_units": 2},
            recommended_facility={"type": "burn_unit", "reason": "Burn injuries present"},
            input_sources=["text"],
            confidence_score=0.9,
        )
        assert report.incident_id == "test-123"
        assert report.severity.score == 4
        assert report.incident_type == "FIRE"

    def test_unknown_incident_type_normalizes_to_other(self):
        from backend.models.output_models import TriageReport
        report = TriageReport(
            incident_id="test-456",
            timestamp="2026-03-28T12:00:00Z",
            incident_type="ZOMBIE_APOCALYPSE",
            severity={"score": 5, "justification": "Extreme"},
            summary="Unknown incident",
            extracted_details={},
        )
        assert report.incident_type == "OTHER"

    def test_caller_state_normalizes_unknown_value(self):
        from backend.models.output_models import ExtractedDetails
        details = ExtractedDetails(caller_emotional_state="terrified")
        assert details.caller_emotional_state == "unknown"

    def test_caller_state_accepts_valid_value(self):
        from backend.models.output_models import ExtractedDetails
        details = ExtractedDetails(caller_emotional_state="panicked")
        assert details.caller_emotional_state == "panicked"

    def test_severity_score_bounds(self):
        from backend.models.output_models import SeverityAssessment
        for score in [1, 2, 3, 4, 5]:
            s = SeverityAssessment(score=score, justification=f"Score {score}")
            assert s.score == score

    def test_severity_score_rejects_out_of_range(self):
        from backend.models.output_models import SeverityAssessment
        with pytest.raises(Exception):
            SeverityAssessment(score=0, justification="Too low")
        with pytest.raises(Exception):
            SeverityAssessment(score=6, justification="Too high")

    def test_resources_defaults_to_zero(self):
        from backend.models.output_models import ResourcesNeeded
        r = ResourcesNeeded()
        assert r.ambulances == 0
        assert r.fire_trucks == 0
        assert r.police_units == 0
        assert r.specialized == []

    def test_confidence_score_range(self):
        from backend.models.output_models import TriageReport
        report = TriageReport(
            incident_id="test-789",
            timestamp="2026-03-28T12:00:00Z",
            incident_type="MEDICAL",
            severity={"score": 2, "justification": "Minor"},
            summary="Minor injury",
            extracted_details={},
            confidence_score=0.95,
        )
        assert 0.0 <= report.confidence_score <= 1.0
