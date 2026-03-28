"""
TriageAI — Emergency & Disaster Response Triage System
Main FastAPI Application

Accepts multimodal inputs (text, voice, PDF documents),
enriches with weather & news context, and produces
structured triage reports using Google Gemini AI.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config.settings import settings
from backend.utils.logger import setup_logging
from backend.utils.validators import (
    sanitize_text,
    validate_audio_file,
    validate_document_file,
    extract_location_hints,
)
from backend.models.output_models import TriageReport, TriageResponse
from backend.services.gemini_service import gemini_service
from backend.services.speech_service import speech_service
from backend.services.document_service import document_service
from backend.services.weather_service import weather_service
from backend.services.news_service import news_service
from backend.services.maps_service import maps_service

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title="TriageAI",
    description="Emergency & Disaster Response Triage System powered by Google Gemini AI",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# In-memory report storage (would be Firestore in production)
reports_store: dict[str, dict] = {}


# --- Routes ---

@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TriageAI",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gcp_project": settings.google_cloud_project or "not configured",
    }


@app.post("/api/triage", response_model=TriageResponse)
async def analyze_triage(
    text: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    voice_file: Optional[UploadFile] = File(None),
    document_file: Optional[UploadFile] = File(None),
):
    """
    Main triage analysis endpoint.

    Accepts multimodal input (text, voice audio, PDF document),
    enriches with weather and news context, and returns a
    structured triage report.
    """
    start_time = time.time()

    # Validate at least one input is provided
    has_text = text and text.strip()
    has_voice = voice_file is not None
    has_document = document_file is not None

    if not has_text and not has_voice and not has_document:
        raise HTTPException(
            status_code=400,
            detail="At least one input is required: text, voice recording, or document",
        )

    logger.info(
        f"Triage request received — text={has_text}, voice={has_voice}, "
        f"document={has_document}, location={location}"
    )

    # Track input sources
    input_sources = []
    raw_inputs = {}

    # --- Process Text Input ---
    text_input = None
    if has_text:
        text_input = sanitize_text(text)
        input_sources.append("text")
        raw_inputs["text"] = text_input[:200] + "..." if len(text_input) > 200 else text_input

    # --- Process Voice Input ---
    voice_transcript = None
    if has_voice:
        # Validate the audio file
        voice_bytes = await voice_file.read()
        is_valid, error_msg = validate_audio_file(
            voice_file.content_type, len(voice_bytes)
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {error_msg}")

        try:
            # Determine encoding from content type
            encoding_map = {
                "audio/webm": "WEBM_OPUS",
                "audio/wav": "LINEAR16",
                "audio/mpeg": "MP3",
                "audio/mp3": "MP3",
                "audio/ogg": "OGG_OPUS",
            }
            encoding = encoding_map.get(voice_file.content_type, "WEBM_OPUS")

            voice_transcript = await speech_service.transcribe_audio(
                audio_bytes=voice_bytes,
                encoding=encoding,
            )
            if voice_transcript:
                input_sources.append("voice")
                raw_inputs["voice_transcript"] = voice_transcript
                logger.info(f"Voice transcribed: '{voice_transcript[:100]}...'")
            else:
                logger.warning("Voice transcription returned empty result")

        except Exception as e:
            logger.error(f"Voice transcription failed: {e}")
            # Don't fail the entire request — continue with other inputs
            raw_inputs["voice_error"] = str(e)

    # --- Process Document Input ---
    document_text = None
    if has_document:
        doc_bytes = await document_file.read()
        is_valid, error_msg = validate_document_file(
            document_file.content_type, len(doc_bytes)
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid document: {error_msg}")

        try:
            document_text = await document_service.extract_text_from_pdf(doc_bytes)
            if document_text:
                input_sources.append("document")
                raw_inputs["document_excerpt"] = document_text[:200] + "..."
                logger.info(f"Document parsed: {len(document_text)} chars")
            else:
                logger.warning("Document extraction returned empty result")

        except Exception as e:
            logger.error(f"Document extraction failed: {e}")
            raw_inputs["document_error"] = str(e)

    # --- Determine Location ---
    # Try to extract location from inputs if not explicitly provided
    if not location:
        for source_text in [text_input, voice_transcript, document_text]:
            if source_text:
                hint = extract_location_hints(source_text)
                if hint:
                    location = hint
                    logger.info(f"Location extracted from text: '{location}'")
                    break

    # --- Enrich with Weather Data ---
    weather_data = None
    if location:
        try:
            weather_data = await weather_service.get_weather_for_location(location)
        except Exception as e:
            logger.error(f"Weather enrichment failed: {e}")

    # --- Enrich with News Data ---
    news_data = None
    try:
        # Build keywords from available context
        keywords = []
        if location:
            keywords.append(location)
        keywords.extend(["emergency", "disaster", "incident"])

        news_data = await news_service.get_relevant_news(
            location=location,
            incident_keywords=" ".join(keywords[:3]),
        )
    except Exception as e:
        logger.error(f"News enrichment failed: {e}")

    # --- Call Gemini AI ---
    try:
        ai_result = await gemini_service.analyze_emergency(
            text_input=text_input,
            voice_transcript=voice_transcript,
            document_text=document_text,
            weather_data=weather_data,
            news_data=news_data,
            location=location,
        )
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        processing_time = (time.time() - start_time) * 1000
        return TriageResponse(
            success=False,
            error=f"AI analysis failed: {str(e)}",
            processing_time_ms=processing_time,
        )

    # --- Build Triage Report ---
    incident_id = str(uuid.uuid4())[:12]
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        report = TriageReport(
            incident_id=incident_id,
            timestamp=timestamp,
            incident_type=ai_result.get("incident_type", "OTHER"),
            severity=ai_result.get("severity", {"score": 3, "justification": "Unable to assess"}),
            summary=ai_result.get("summary", "Emergency report received — details being processed"),
            extracted_details=ai_result.get("extracted_details", {}),
            immediate_actions=ai_result.get("immediate_actions", []),
            resources_needed=ai_result.get("resources_needed", {}),
            recommended_facility=ai_result.get("recommended_facility", {}),
            weather_context={
                "temperature": f"{weather_data['temperature_c']}°C" if weather_data else None,
                "conditions": weather_data.get("conditions") if weather_data else None,
                "wind_speed": f"{weather_data['wind_speed_mps']} m/s" if weather_data else None,
                "alerts": weather_data.get("alerts", []) if weather_data else [],
                "impact_assessment": None,
            } if weather_data else None,
            news_context={
                "related_incidents": news_data[:3] if news_data else [],
                "area_alerts": [],
            } if news_data else None,
            input_sources=input_sources,
            raw_inputs=raw_inputs,
            confidence_score=ai_result.get("confidence_score", 0.7),
        )

        # Store report
        reports_store[incident_id] = report.model_dump()

        processing_time = (time.time() - start_time) * 1000
        logger.info(
            f"Triage complete: incident={incident_id}, "
            f"severity={report.severity.score}, "
            f"time={processing_time:.0f}ms"
        )

        return TriageResponse(
            success=True,
            report=report,
            processing_time_ms=round(processing_time, 2),
        )

    except Exception as e:
        logger.error(f"Report building failed: {e}")
        processing_time = (time.time() - start_time) * 1000
        return TriageResponse(
            success=False,
            error=f"Failed to build report: {str(e)}",
            processing_time_ms=processing_time,
        )


@app.get("/api/reports")
async def list_reports():
    """List all stored triage reports."""
    reports = []
    for rid, report in reports_store.items():
        reports.append({
            "incident_id": rid,
            "timestamp": report.get("timestamp"),
            "incident_type": report.get("incident_type"),
            "severity_score": report.get("severity", {}).get("score"),
            "summary": report.get("summary", "")[:100],
        })

    return {
        "total": len(reports),
        "reports": sorted(reports, key=lambda r: r["timestamp"], reverse=True),
    }


@app.get("/api/reports/{incident_id}")
async def get_report(incident_id: str):
    """Get a specific triage report by ID."""
    report = reports_store.get(incident_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# --- Run ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=True,
    )
