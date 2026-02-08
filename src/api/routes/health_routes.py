"""
Health Routes

Used for:
- Liveness checks (is the app running?)
- Readiness checks (are dependencies reachable?)
- Deployment monitoring (load balancers, uptime checks)
"""

from fastapi import APIRouter, status
from typing import Dict

from src.config.settings import get_settings
from src.utils.time_utils import utc_now_iso

router = APIRouter()
settings = get_settings()


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe.

    Indicates whether the API process is running.
    Used by:
    - Kubernetes
    - Load balancers
    - Basic uptime monitoring
    """

    return {
        "status": "UP",
        "service": settings.APP_NAME,
        "timestamp": utc_now_iso(),
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
)
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe.

    Indicates whether the API is ready to serve traffic.
    This should fail if critical dependencies are unavailable.
    """

    # In future you can add checks like:
    # - Vector store availability
    # - Disk write access
    # - External API connectivity

    return {
        "status": "READY",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": utc_now_iso(),
    }
