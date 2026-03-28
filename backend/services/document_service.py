"""Document Parsing Service — Extracts text from PDFs."""

import io
import logging
from typing import Optional

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class DocumentService:
    """Handles PDF document text extraction."""

    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_bytes: Raw PDF file bytes

        Returns:
            Extracted text from all pages
        """
        logger.info(f"Extracting text from PDF ({len(pdf_bytes)} bytes)")

        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            pages_text = []

            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append(f"[Page {i + 1}]\n{text.strip()}")

            if not pages_text:
                logger.warning("PDF contained no extractable text")
                return ""

            full_text = "\n\n".join(pages_text)

            # Truncate if extremely long (Gemini has context limits)
            max_chars = 15000
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + "\n\n[... document truncated ...]"
                logger.info(f"PDF text truncated to {max_chars} chars")

            logger.info(
                f"PDF extraction complete: {len(reader.pages)} pages, "
                f"{len(full_text)} chars"
            )

            return full_text

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")


# Singleton instance
document_service = DocumentService()
