"""Health and readiness check endpoints."""

from fastapi import APIRouter
from app.config import settings
from app.schemas import HealthResponse, ReadinessResponse
from app.utils.time import utc_now

router = APIRouter(tags=["Health"])


@router.get("/api/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return basic service health."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=utc_now(),
    )


@router.get("/api/ready", response_model=ReadinessResponse)
def get_readiness() -> ReadinessResponse:
    """Check whether external API keys and services are configured."""
    has_supabase = bool(settings.supabase_url and settings.supabase_service_role_key)
    has_gemini = bool(settings.gemini_api_key)
    has_resend = bool(settings.resend_api_key)

    is_ready = has_supabase and has_gemini and has_resend

    return ReadinessResponse(
        ready=is_ready,
        supabase_configured=has_supabase,
        gemini_configured=has_gemini,
        resend_configured=has_resend,
    )
