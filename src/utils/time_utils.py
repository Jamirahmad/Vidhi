"""Time helpers shared across API responses and logs."""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Returns current UTC timestamp in ISO-8601 format with trailing Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
