"""Speech-to-Text Service — Converts audio to text using Google Cloud."""

import io
import logging
from typing import Optional

from google.cloud import speech

logger = logging.getLogger(__name__)


class SpeechService:
    """Handles voice-to-text conversion using Google Cloud Speech-to-Text."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = speech.SpeechClient()
            logger.info("Speech-to-Text client initialized")
        return self._client

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        encoding: str = "WEBM_OPUS",
        sample_rate: int = 48000,
        language_code: str = "en-US",
    ) -> str:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio file bytes
            encoding: Audio encoding format (WEBM_OPUS, LINEAR16, FLAC, etc.)
            sample_rate: Audio sample rate in Hz
            language_code: BCP-47 language code

        Returns:
            Transcribed text string
        """
        client = self._get_client()

        # Map string encoding to enum
        encoding_map = {
            "WEBM_OPUS": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            "LINEAR16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            "FLAC": speech.RecognitionConfig.AudioEncoding.FLAC,
            "MP3": speech.RecognitionConfig.AudioEncoding.MP3,
            "OGG_OPUS": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        }

        audio_encoding = encoding_map.get(
            encoding.upper(),
            speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        )

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=audio_encoding,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="latest_long",
            # Enable enhanced features
            use_enhanced=True,
            # Add speech contexts for emergency-related vocabulary
            speech_contexts=[
                speech.SpeechContext(
                    phrases=[
                        "emergency", "ambulance", "fire", "accident",
                        "injured", "bleeding", "unconscious", "breathing",
                        "heart attack", "stroke", "seizure", "fracture",
                        "trapped", "collision", "explosion", "flood",
                        "earthquake", "tornado", "hurricane",
                    ],
                    boost=10.0,
                )
            ],
        )

        logger.info(
            f"Transcribing audio: {len(audio_bytes)} bytes, "
            f"encoding={encoding}, rate={sample_rate}Hz"
        )

        try:
            response = client.recognize(config=config, audio=audio)

            if not response.results:
                logger.warning("Speech-to-Text returned no results")
                return ""

            # Concatenate all transcription results
            transcript = " ".join(
                result.alternatives[0].transcript
                for result in response.results
                if result.alternatives
            )

            confidence = (
                response.results[0].alternatives[0].confidence
                if response.results and response.results[0].alternatives
                else 0.0
            )

            logger.info(
                f"Transcription complete: {len(transcript)} chars, "
                f"confidence={confidence:.2f}"
            )

            return transcript

        except Exception as e:
            logger.error(f"Speech-to-Text error: {e}")
            raise


# Singleton instance
speech_service = SpeechService()
