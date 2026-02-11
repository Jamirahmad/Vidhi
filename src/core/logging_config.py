# src/core/logging_config.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _safe_mkdir(path: str) -> None:
    """Create directory if it doesn't exist (safe for concurrent calls)."""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        # If directory creation fails, logging should still work via console.
        pass


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "vidhi.log",
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    fmt: str = DEFAULT_LOG_FORMAT,
    datefmt: str = DEFAULT_DATE_FORMAT,
) -> None:
    """
    Centralized logging setup for the Vidhi application.

    Features:
    - Console logging (stdout)
    - Rotating file handler (prevents log file from growing infinitely)
    - Clean formatting
    - Safe directory creation

    This should be called ONCE in the application entrypoint.
    """

    # Normalize log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Prevent duplicate handlers if setup_logging is called multiple times
    if root_logger.handlers:
        return

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if enable_file:
        _safe_mkdir(log_dir)
        file_path = os.path.join(log_dir, log_file)

        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Reduce noisy external library logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


class SecretMaskingFilter(logging.Filter):
    """
    Masks sensitive strings in log messages.

    Example usage:
        setup_logging()
        add_secret_masking_filter(["MY_SECRET_KEY"])
    """

    def __init__(self, secrets: Optional[list[str]] = None):
        super().__init__()
        self.secrets = [s for s in (secrets or []) if s]

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = str(record.getMessage())
            for secret in self.secrets:
                if secret and secret in msg:
                    msg = msg.replace(secret, "***MASKED***")

            # overwrite record.msg safely
            record.msg = msg
            record.args = ()
        except Exception:
            # Never break logging due to masking
            pass

        return True


def add_secret_masking_filter(secrets: list[str]) -> None:
    """
    Adds a masking filter to all handlers on the root logger.
    This ensures secrets do not appear in logs.

    Call after setup_logging().
    """
    root_logger = logging.getLogger()
    masking_filter = SecretMaskingFilter(secrets)

    for handler in root_logger.handlers:
        handler.addFilter(masking_filter)
