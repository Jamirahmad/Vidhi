"""
Local Storage

Filesystem-backed storage abstraction.
Acts as the ground-truth persistence layer for ingestion artifacts.

Use cases:
- raw documents
- parsed text
- metadata JSON
- intermediate pipeline outputs
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class LocalStorageError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# LocalStorage
# ---------------------------------------------------------------------

class LocalStorage:
    """
    Local filesystem storage with atomic writes.
    """

    def __init__(self, base_path: Union[str, Path]) -> None:
        self.base_path = Path(base_path).resolve()
        self._ensure_base()

        logger.info("LocalStorage initialized | base_path=%s", self.base_path)

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def write_bytes(self, relative_path: Union[str, Path], data: bytes) -> Path:
        """
        Write binary data atomically.
        """
        target = self._resolve(relative_path)
        self._atomic_write(target, data, mode="wb")
        logger.debug("Wrote bytes | path=%s | size=%s", target, len(data))
        return target

    def write_text(
        self,
        relative_path: Union[str, Path],
        text: str,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Write text data atomically.
        """
        target = self._resolve(relative_path)
        self._atomic_write(target, text.encode(encoding), mode="wb")
        logger.debug("Wrote text | path=%s | chars=%s", target, len(text))
        return target

    def read_bytes(self, relative_path: Union[str, Path]) -> bytes:
        """
        Read binary data.
        """
        path = self._resolve(relative_path)

        try:
            with open(path, "rb") as f:
                return f.read()
        except Exception as e:
            raise LocalStorageError(f"Failed to read bytes: {path}") from e

    def read_text(
        self,
        relative_path: Union[str, Path],
        encoding: str = "utf-8",
    ) -> str:
        """
        Read text data.
        """
        return self.read_bytes(relative_path).decode(encoding)

    def exists(self, relative_path: Union[str, Path]) -> bool:
        """
        Check if file exists.
        """
        return self._resolve(relative_path).exists()

    def delete(self, relative_path: Union[str, Path]) -> None:
        """
        Delete file if exists.
        """
        path = self._resolve(relative_path)

        if path.exists():
            path.unlink()
            logger.debug("Deleted | path=%s", path)

    def list_files(self, relative_path: Union[str, Path] = "") -> list[Path]:
        """
        List files under a directory.
        """
        path = self._resolve(relative_path)

        if not path.exists():
            return []

        return [p for p in path.rglob("*") if p.is_file()]

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

    def _ensure_base(self) -> None:
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise LocalStorageError(
                f"Failed to create base directory: {self.base_path}"
            ) from e

    def _resolve(self, relative_path: Union[str, Path]) -> Path:
        """
        Resolve and validate relative path to prevent traversal.
        """
        resolved = (self.base_path / relative_path).resolve()

        if not str(resolved).startswith(str(self.base_path)):
            raise LocalStorageError("Path traversal detected")

        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

    def _atomic_write(self, path: Path, data: bytes, mode: str) -> None:
        """
        Atomic write using temp file + rename.
        """
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                dir=str(path.parent),
            ) as tmp:
                tmp.write(data)
                tmp.flush()
                os.fsync(tmp.fileno())

            shutil.move(tmp.name, path)
        except Exception as e:
            raise LocalStorageError(f"Atomic write failed: {path}") from e
