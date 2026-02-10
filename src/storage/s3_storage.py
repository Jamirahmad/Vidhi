"""
S3 Storage

Amazon S3-backed storage abstraction.
Designed to mirror LocalStorage behavior for seamless backend swapping.

Use cases:
- raw document persistence
- parsed text storage
- metadata artifacts
- long-term, durable storage
"""

from __future__ import annotations

import posixpath
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class S3StorageError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# S3Storage
# ---------------------------------------------------------------------

class S3Storage:
    """
    S3-backed storage with a LocalStorage-like API.
    """

    def __init__(
        self,
        *,
        bucket_name: str,
        base_prefix: str = "",
        region_name: Optional[str] = None,
        s3_client: Optional[boto3.client] = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.base_prefix = self._normalize_prefix(base_prefix)

        self._s3 = s3_client or boto3.client(
            "s3",
            region_name=region_name,
        )

        logger.info(
            "S3Storage initialized | bucket=%s | prefix=%s",
            bucket_name,
            self.base_prefix or "/",
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def write_bytes(self, relative_path: str, data: bytes) -> str:
        """
        Upload binary data to S3.
        """
        key = self._resolve_key(relative_path)

        try:
            self._s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
            )
            logger.debug(
                "S3 write bytes | bucket=%s | key=%s | size=%s",
                self.bucket_name,
                key,
                len(data),
            )
            return key
        except (BotoCoreError, ClientError) as e:
            raise S3StorageError(f"Failed to write bytes: s3://{self.bucket_name}/{key}") from e

    def write_text(
        self,
        relative_path: str,
        text: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        Upload text data to S3.
        """
        return self.write_bytes(relative_path, text.encode(encoding))

    def read_bytes(self, relative_path: str) -> bytes:
        """
        Download binary data from S3.
        """
        key = self._resolve_key(relative_path)

        try:
            response = self._s3.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return response["Body"].read()
        except (BotoCoreError, ClientError) as e:
            raise S3StorageError(f"Failed to read bytes: s3://{self.bucket_name}/{key}") from e

    def read_text(
        self,
        relative_path: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        Download text data from S3.
        """
        return self.read_bytes(relative_path).decode(encoding)

    def exists(self, relative_path: str) -> bool:
        """
        Check if object exists in S3.
        """
        key = self._resolve_key(relative_path)

        try:
            self._s3.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise S3StorageError(
                f"Failed to check existence: s3://{self.bucket_name}/{key}"
            ) from e

    def delete(self, relative_path: str) -> None:
        """
        Delete object from S3.
        """
        key = self._resolve_key(relative_path)

        try:
            self._s3.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            logger.debug(
                "S3 delete | bucket=%s | key=%s",
                self.bucket_name,
                key,
            )
        except (BotoCoreError, ClientError) as e:
            raise S3StorageError(
                f"Failed to delete: s3://{self.bucket_name}/{key}"
            ) from e

    def list_files(self, relative_path: str = "") -> list[str]:
        """
        List objects under a prefix.
        """
        prefix = self._resolve_key(relative_path)

        try:
            paginator = self._s3.get_paginator("list_objects_v2")
            results = []

            for page in paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
            ):
                for obj in page.get("Contents", []):
                    results.append(obj["Key"])

            return results
        except (BotoCoreError, ClientError) as e:
            raise S3StorageError(
                f"Failed to list objects: s3://{self.bucket_name}/{prefix}"
            ) from e

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

    def _normalize_prefix(self, prefix: str) -> str:
        if not prefix:
            return ""
        return prefix.strip("/")

    def _resolve_key(self, relative_path: str) -> str:
        """
        Resolve S3 object key safely.
        """
        relative = relative_path.lstrip("/")

        if ".." in relative.split("/"):
            raise S3StorageError("Path traversal detected in S3 key")

        if self.base_prefix:
            return posixpath.join(self.base_prefix, relative)

        return relative
