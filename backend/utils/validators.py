"""Input validators and sanitizers for TriageAI."""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/wav", "audio/mpeg", "audio/ogg", "audio/mp3"}
ALLOWED_DOC_TYPES = {"application/pdf"}

# Max sizes
MAX_AUDIO_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_DOC_SIZE = 10 * 1024 * 1024     # 10 MB
MAX_TEXT_LENGTH = 5000


def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks.

    Removes potentially dangerous patterns while preserving
    meaningful emergency information.
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove excessive whitespace but preserve single newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Truncate if too long
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
        logger.warning(f"Text input truncated to {MAX_TEXT_LENGTH} chars")

    return text


def validate_audio_file(
    content_type: Optional[str],
    file_size: int,
) -> tuple[bool, str]:
    """
    Validate an uploaded audio file.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content_type:
        return False, "No content type specified for audio file"

    if content_type not in ALLOWED_AUDIO_TYPES:
        return False, f"Unsupported audio format: {content_type}. Allowed: {ALLOWED_AUDIO_TYPES}"

    if file_size > MAX_AUDIO_SIZE:
        return False, f"Audio file too large: {file_size} bytes. Max: {MAX_AUDIO_SIZE} bytes"

    if file_size == 0:
        return False, "Audio file is empty"

    return True, ""


def validate_document_file(
    content_type: Optional[str],
    file_size: int,
) -> tuple[bool, str]:
    """
    Validate an uploaded document file.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content_type:
        return False, "No content type specified for document"

    if content_type not in ALLOWED_DOC_TYPES:
        return False, f"Unsupported document format: {content_type}. Allowed: {ALLOWED_DOC_TYPES}"

    if file_size > MAX_DOC_SIZE:
        return False, f"Document too large: {file_size} bytes. Max: {MAX_DOC_SIZE} bytes"

    if file_size == 0:
        return False, "Document file is empty"

    return True, ""


def extract_location_hints(text: str) -> Optional[str]:
    """
    Try to extract location hints from free text.

    Looks for common patterns like "at [location]", "near [location]",
    "in [city]", street addresses, etc.
    """
    if not text:
        return None

    # Common location patterns
    patterns = [
        r"(?:at|near|in|on|around)\s+(\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|highway|hwy))",
        r"(?:at|near|in|on|around)\s+([\w\s]+(?:city|town|village|district|county))",
        r"(\d+\s+[\w\s]+,\s*[\w\s]+,\s*[A-Z]{2}\s*\d{5})",  # US address
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None
