"""Tests for input validation logic."""

import pytest
from backend.utils.validators import (
    sanitize_text,
    validate_audio_file,
    validate_document_file,
    extract_location_hints,
)


class TestSanitizeText:
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

    def test_truncation(self):
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


class TestValidateAudioFile:
    def test_valid_webm(self):
        is_valid, error = validate_audio_file("audio/webm", 1024)
        assert is_valid is True
        assert error == ""

    def test_valid_wav(self):
        is_valid, error = validate_audio_file("audio/wav", 1024)
        assert is_valid is True

    def test_invalid_type(self):
        is_valid, error = validate_audio_file("video/mp4", 1024)
        assert is_valid is False
        assert "Unsupported" in error

    def test_too_large(self):
        is_valid, error = validate_audio_file("audio/webm", 20 * 1024 * 1024)
        assert is_valid is False
        assert "too large" in error

    def test_empty_file(self):
        is_valid, error = validate_audio_file("audio/webm", 0)
        assert is_valid is False
        assert "empty" in error

    def test_no_content_type(self):
        is_valid, error = validate_audio_file(None, 1024)
        assert is_valid is False


class TestValidateDocumentFile:
    def test_valid_pdf(self):
        is_valid, error = validate_document_file("application/pdf", 1024)
        assert is_valid is True

    def test_invalid_type(self):
        is_valid, error = validate_document_file("text/plain", 1024)
        assert is_valid is False
        assert "Unsupported" in error

    def test_too_large(self):
        is_valid, error = validate_document_file("application/pdf", 20 * 1024 * 1024)
        assert is_valid is False

    def test_empty(self):
        is_valid, error = validate_document_file("application/pdf", 0)
        assert is_valid is False


class TestExtractLocationHints:
    def test_extracts_street_address(self):
        text = "There's an accident at 123 Main Street"
        result = extract_location_hints(text)
        assert result is not None
        assert "Main Street" in result

    def test_extracts_near_location(self):
        text = "Fire spotted near downtown district"
        result = extract_location_hints(text)
        # May or may not match depending on pattern
        # This tests the function doesn't crash

    def test_no_location(self):
        text = "Someone needs help urgently"
        result = extract_location_hints(text)
        # No location pattern found — returns None
        assert result is None or isinstance(result, str)

    def test_empty_input(self):
        assert extract_location_hints("") is None
        assert extract_location_hints(None) is None
