"""Input validation models for TriageAI API."""

from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class InputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    DOCUMENT = "document"


class TriageTextRequest(BaseModel):
    """Request model for text-based triage input."""
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Emergency description text"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional location information"
    )

    @validator("text")
    def sanitize_text(cls, v):
        """Basic input sanitization."""
        # Strip dangerous characters but keep meaningful content
        v = v.strip()
        if not v:
            raise ValueError("Text input cannot be empty")
        return v


class TriageVoiceRequest(BaseModel):
    """Metadata for voice-based triage input (file sent as form data)."""
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional location information"
    )


class TriageDocumentRequest(BaseModel):
    """Metadata for document-based triage input (file sent as form data)."""
    context: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional context about the document"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional location information"
    )


class MultiModalTriageRequest(BaseModel):
    """Combined multimodal triage request."""
    text: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=200)
    # Voice and document files are handled via form data, not JSON
