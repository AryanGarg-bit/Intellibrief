"""Unit tests for health and readiness routes (direct function tests)."""

from app.routes.health import get_health, get_readiness
from app.main import serve_index


def test_root_endpoint():
    """Verify that root endpoint serves the HTML frontend."""
    response = serve_index()
    assert response.status_code == 200
    assert "IntelliBrief" in response.body.decode("utf-8")



def test_health_endpoint():
    """Verify that get_health() returns status ok and a valid timestamp."""
    response = get_health()
    assert response.status == "ok"
    assert response.version == "0.1.0"
    assert response.timestamp is not None


def test_readiness_endpoint_default():
    """Verify that get_readiness() correctly reports missing configuration."""
    response = get_readiness()
    assert response.ready is False
    assert response.supabase_configured is False
    assert response.gemini_configured is False
    assert response.resend_configured is False
