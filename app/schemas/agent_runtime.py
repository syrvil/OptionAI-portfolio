"""Operational metadata shared by all LLM agents."""

from pydantic import BaseModel, Field


class AgentRuntimeMetadata(BaseModel):
    """Non-sensitive information about one agent execution."""

    provider: str | None = None
    model: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)
    token_usage: dict[str, object] = Field(default_factory=dict)
    cache_status: str = "not_used"
    input_fingerprint: str | None = None
    error: str | None = None
