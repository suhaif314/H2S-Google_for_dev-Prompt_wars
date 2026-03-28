"""Structured logging setup for TriageAI."""

import logging
import sys


def setup_logging(level: str = "INFO"):
    """Configure structured logging for the application."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("triageai")
    logger.info("TriageAI logging initialized")
    return logger
