"""Offline tests for the FastAPI application shell."""

from app.api.main import health


def test_health_endpoint() -> None:
    assert health() == {"status": "ok"}
