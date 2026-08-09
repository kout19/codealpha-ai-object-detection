"""Application-wide logging configuration.

This module configures Python's standard `logging` module once, at
application startup, and exposes a `get_logger()` helper that every other
module should use to obtain a logger instance.
"""

import logging
import sys

from app.core.config import get_settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """Configure the root logger for the entire application."""
    settings = get_settings()

    numeric_level = getattr(logging, settings.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(
            f"Invalid log_level '{settings.log_level}' in settings. "
            "Expected one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(
        logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )

    root_logger.addHandler(console_handler)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)

    root_logger.info(
        "Logging configured successfully at level '%s'.", settings.log_level
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for use within a specific module."""
    return logging.getLogger(name)