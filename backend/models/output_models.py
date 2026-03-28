"""Output models for TriageAI structured triage reports."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class IncidentType(str, Enum):
    MEDICAL = "MEDICAL"
    FIRE = "FIRE"
    ACCIDENT = "ACCIDENT"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    VIOLENCE = "VIOLENCE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    HAZMAT = "HAZMAT"
    OTHER = "OTHER"


class CallerState(str, Enum):
    CALM = "calm"
    CONCERNED = "concerned"
    DISTRESSED = "distressed"
    PANICKED = "panicked"
    INCOHERENT = "incoherent"
    UNKNOWN = "unknown"


class SeverityAssessment(BaseModel):
    """Severity scoring with justification."""
    score: int = Field(..., ge=1, le=5, description="1=minor, 5=life-threatening")
    justification: str = Field(..., description="Why this severity level was assigned")


class ExtractedDetails(BaseModel):
    """Structured details extracted from the emergency report."""
    location: str = Field(default="unknown")
    num_affected: str = Field(default="unknown")
    injuries_described: list[str] = Field(default_factory=list)
    hazards_present: list[str] = Field(default_factory=list)
    caller_emotional_state: str = Field(default="unknown")

    @field_validator("caller_emotional_state", mode="before")
    @classmethod
    def normalize_caller_state(cls, v):
        """Accept any string, normalize to known values."""
        if isinstance(v, str):
            v = v.lower().strip()
            valid = {"calm", "concerned", "distressed", "panicked", "incoherent", "unknown"}
            return v if v in valid else "unknown"
        return "unknown"


class ImmediateAction(BaseModel):
    """A prioritized action to take."""
    priority: int = Field(..., ge=1, le=10)
    action: str
    responsible_party: str


class ResourcesNeeded(BaseModel):
    """Resources required for the emergency response."""
    ambulances: int = Field(default=0, ge=0)
    fire_trucks: int = Field(default=0, ge=0)
    police_units: int = Field(default=0, ge=0)
    specialized: list[str] = Field(default_factory=list)


class RecommendedFacility(BaseModel):
    """Recommended facility type and reason."""
    type: str = Field(default="hospital")
    reason: str = Field(default="General medical facility")


class WeatherContext(BaseModel):
    """Weather data relevant to the incident."""
    temperature: Optional[str] = None
    conditions: Optional[str] = None
    wind_speed: Optional[str] = None
    alerts: list[str] = Field(default_factory=list)
    impact_assessment: Optional[str] = None


class NewsContext(BaseModel):
    """Related news articles for situational awareness."""
    related_incidents: list[str] = Field(default_factory=list)
    area_alerts: list[str] = Field(default_factory=list)


class TriageReport(BaseModel):
    """Complete structured triage report — the main output."""
    incident_id: str
    timestamp: str
    incident_type: str = Field(default="OTHER")
    severity: SeverityAssessment
    summary: str
    extracted_details: ExtractedDetails
    immediate_actions: list[ImmediateAction] = Field(default_factory=list)
    resources_needed: ResourcesNeeded = Field(default_factory=ResourcesNeeded)
    recommended_facility: RecommendedFacility = Field(default_factory=RecommendedFacility)
    weather_context: Optional[WeatherContext] = None
    news_context: Optional[NewsContext] = None
    input_sources: list[str] = Field(default_factory=list)
    raw_inputs: dict = Field(default_factory=dict)
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)

    @field_validator("incident_type", mode="before")
    @classmethod
    def normalize_incident_type(cls, v):
        """Accept any string for incident_type."""
        valid = {"MEDICAL", "FIRE", "ACCIDENT", "NATURAL_DISASTER", "VIOLENCE", "INFRASTRUCTURE", "HAZMAT", "OTHER"}
        if isinstance(v, str):
            v = v.upper().strip()
            return v if v in valid else "OTHER"
        return "OTHER"


class TriageResponse(BaseModel):
    """API response wrapper."""
    success: bool
    report: Optional[TriageReport] = None
    error: Optional[str] = None
    processing_time_ms: float = 0
