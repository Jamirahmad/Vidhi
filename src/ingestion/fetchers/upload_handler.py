"""
Upload Handler

Handles user-uploaded documents and converts them into
raw ingestion records compatible with the ingestion pipeline.

Supported inputs:
- PDF
- DOCX
- TXT
- HTML

Aligned with:
- src/ingestion/fetchers/*
- src/ingestion/parsers/*
- ingestion metadata-first architecture
"""

from __future__ import annotations

import mimetypes
import time
from pathlib import Path
from typing import Dict, Iterable, Optional, Union

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------

class UploadError(Exception):
    """Base error for upload handling."""


# ---------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------

class UploadHandler:
    """
    Handles ingestion of user-uploaded files.
    """

    DEFAULT_ALLOWED_MIME_TYPES = {
        "application/pdf",
        "text/plain",
        "text/html",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(
        self,
        *,
        allowed_mime_types: Optional[set[str]] = None,
        max_file_size_mb: int = 25,
    ) -> None:
        self.allowed_mime_types = (
            allowed_mime_types or self.DEFAULT_ALLOWED_MIME_TYPES
        )
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def handle_file(
        self,
        *,
        file_path: Union[str, Path],
        source_label: str = "upload",
        extra_metadata: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        """
        Handle a single uploaded file and return a raw ingestion record.

        Output format:
        {
            "id": str,
            "source": "upload",
            "path": str,
            "bytes": bytes,
            "metadata": dict
        }
        """
        path = Path(file_path)

        if not path.exists():
            raise UploadError(f"File does not exist: {path}")

        file_size = path.stat().st_size
        if file_size > self.max_file_size_bytes:
            raise UploadError(
                f"File too large ({file_size} bytes): {path.name}"
            )

        mime_type, _ = mimetypes.guess_type(path.name)
        if mime_type not in self.allowed_mime_types:
            raise UploadError(
                f"Unsupported file type: {mime_type or 'unknown'}"
            )

        try:
            file_bytes = path.read_bytes()
        except Exception as exc:
            raise UploadError(
                f"Failed to read uploaded file: {path.name}"
            ) from exc

        metadata = {
            "source": source_label,
            "file_name": path.name,
            "mime_type": mime_type,
            "file_size_bytes": file_size,
            "upload_ts": time.time(),
        }

        if extra_metadata:
            metadata.update(extra_metadata)

        logger.info(
            "Handled uploaded file | name=%s | size=%s bytes | type=%s",
            path.name,
            file_size,
            mime_type,
        )

        return {
            "id": str(path.resolve()),
            "source": source_label,
            "path": str(path.resolve()),
            "bytes": file_bytes,
            "metadata": metadata,
        }

    def handle_files(
        self,
        *,
        files: Iterable[Union[str, Path]],
        source_label: str = "upload",
        extra_metadata: Optional[Dict[str, object]] = None,
    ) -> Iterable[Dict[str, object]]:
        """
        Handle multiple uploaded files.
        """
        for file_path in files:
            try:
                yield self.handle_file(
                    file_path=file_path,
                    source_label=source_label,
                    extra_metadata=extra_metadata,
                )
            except UploadError as exc:
                logger.warning(str(exc))
                continue
