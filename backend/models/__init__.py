"""Models package."""
from .input_models import (
    InputType,
    TriageTextRequest,
    TriageVoiceRequest,
    TriageDocumentRequest,
    MultiModalTriageRequest,
)
from .output_models import (
    TriageReport,
    TriageResponse,
    IncidentType,
    SeverityAssessment,
    ExtractedDetails,
    ImmediateAction,
    ResourcesNeeded,
    RecommendedFacility,
    WeatherContext,
    NewsContext,
)

__all__ = [
    "InputType",
    "TriageTextRequest",
    "TriageVoiceRequest",
    "TriageDocumentRequest",
    "MultiModalTriageRequest",
    "TriageReport",
    "TriageResponse",
    "IncidentType",
    "SeverityAssessment",
    "ExtractedDetails",
    "ImmediateAction",
    "ResourcesNeeded",
    "RecommendedFacility",
    "WeatherContext",
    "NewsContext",
]
