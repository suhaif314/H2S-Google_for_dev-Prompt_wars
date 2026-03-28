"""Gemini AI Service — Core intelligence engine for TriageAI."""

import json
import logging
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel, Part

from backend.config.settings import settings
from backend.prompts.triage_prompt import TRIAGE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiService:
    """Handles all interactions with Google Gemini via Vertex AI."""

    def __init__(self):
        self._model = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of Vertex AI and Gemini model."""
        if not self._initialized:
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.google_cloud_location,
            )
            self._model = GenerativeModel(
                model_name=settings.gemini_model,
                system_instruction=TRIAGE_SYSTEM_PROMPT,
            )
            self._initialized = True
            logger.info(
                f"Gemini initialized: project={settings.google_cloud_project}, "
                f"model={settings.gemini_model}"
            )

    def _build_prompt(
        self,
        text_input: Optional[str] = None,
        voice_transcript: Optional[str] = None,
        document_text: Optional[str] = None,
        weather_data: Optional[dict] = None,
        news_data: Optional[list] = None,
        location: Optional[str] = None,
    ) -> str:
        """Build a comprehensive prompt combining all input sources."""
        sections = []

        if text_input:
            sections.append(
                f"=== DIRECT TEXT REPORT ===\n{text_input}"
            )

        if voice_transcript:
            sections.append(
                f"=== TRANSCRIBED VOICE RECORDING ===\n"
                f"(Note: This was spoken by a caller. Interpret tone and urgency.)\n"
                f"{voice_transcript}"
            )

        if document_text:
            sections.append(
                f"=== EXTRACTED DOCUMENT TEXT ===\n"
                f"(From uploaded PDF/document)\n"
                f"{document_text}"
            )

        if weather_data:
            weather_str = json.dumps(weather_data, indent=2)
            sections.append(
                f"=== CURRENT WEATHER CONDITIONS ===\n"
                f"Location: {location or 'Not specified'}\n"
                f"{weather_str}"
            )

        if news_data:
            news_str = "\n".join(
                [f"- {article}" for article in news_data[:5]]
            )
            sections.append(
                f"=== RECENT RELATED NEWS ===\n"
                f"(Latest news from the area for context)\n"
                f"{news_str}"
            )

        if location:
            sections.append(
                f"=== REPORTED LOCATION ===\n{location}"
            )

        combined = "\n\n".join(sections)

        return (
            f"Analyze the following emergency report and provide a structured "
            f"triage assessment as JSON:\n\n{combined}\n\n"
            f"Respond with ONLY valid JSON matching the specified schema."
        )

    async def analyze_emergency(
        self,
        text_input: Optional[str] = None,
        voice_transcript: Optional[str] = None,
        document_text: Optional[str] = None,
        weather_data: Optional[dict] = None,
        news_data: Optional[list] = None,
        location: Optional[str] = None,
    ) -> dict:
        """
        Analyze emergency inputs and produce structured triage report.

        Combines all available inputs into a single prompt, sends to Gemini,
        and parses the structured JSON response.
        """
        self._initialize()

        prompt = self._build_prompt(
            text_input=text_input,
            voice_transcript=voice_transcript,
            document_text=document_text,
            weather_data=weather_data,
            news_data=news_data,
            location=location,
        )

        logger.info(f"Sending prompt to Gemini ({len(prompt)} chars)")

        try:
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,       # Low temp for consistent structured output
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
            )

            response_text = response.text.strip()
            logger.info(f"Gemini response received ({len(response_text)} chars)")

            # Parse JSON response
            # Handle potential markdown code blocks in response
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0]
                response_text = response_text.strip()

            result = json.loads(response_text)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Raw response: {response_text[:500]}")
            raise ValueError(f"Gemini returned invalid JSON: {e}")

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


# Singleton instance
gemini_service = GeminiService()
