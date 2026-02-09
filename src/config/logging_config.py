"""
Logging Configuration

Centralized logging setup for Vidhi.
Supports:
- Application logs
- Agent-level trace logs
- Structured, timestamped output
"""

import logging
import logging.config
from pathlib import Path

from src.config.constants import (
    APP_LOG_FILE,
    AGENT_TRACE_LOG_FILE,
    UTF8_ENCODING,
)


# -------------------------------------------------------------------
# Ensure log directories exist
# -------------------------------------------------------------------

def _ensure_log_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


_ensure_log_dir(APP_LOG_FILE)
_ensure_log_dir(AGENT_TRACE_LOG_FILE)


# -------------------------------------------------------------------
# Logging Configuration Dictionary
# -------------------------------------------------------------------

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            )
        },
        "agent_trace": {
            "format": (
                "%(asctime)s | TRACE=%(trace_id)s | "
                "REQ=%(request_id)s | AGENT=%(agent)s | "
                "STATUS=%(status)s | %(message)s"
            )
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },

        "app_file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": APP_LOG_FILE,
            "encoding": UTF8_ENCODING,
            "level": "INFO",
        },

        "agent_trace_file": {
            "class": "logging.FileHandler",
            "formatter": "agent_trace",
            "filename": AGENT_TRACE_LOG_FILE,
            "encoding": UTF8_ENCODING,
            "level": "INFO",
        },
    },

    "loggers": {
        # Application-level logs
        "vidhi": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },

        # Agent-level trace logger
        "vidhi.agent_trace": {
            "handlers": ["agent_trace_file"],
            "level": "INFO",
            "propagate": False,
        },
    },

    "root": {
        "handlers": ["console", "app_file"],
        "level": "WARNING",
    },
}


# -------------------------------------------------------------------
# Initialization Helpers
# -------------------------------------------------------------------

def setup_logging() -> None:
    """
    Initialize logging configuration.
    Should be called once at application startup.
    """
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a standard application logger.
    """
    return logging.getLogger(name)


def get_agent_trace_logger() -> logging.Logger:
    """
    Retrieve the dedicated agent trace logger.
    """
    return logging.getLogger("vidhi.agent_trace")
