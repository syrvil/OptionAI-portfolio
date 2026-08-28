"""Centralized, environment-based application configuration."""

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Values use the ``OPTIONAI_`` prefix. For example,
    ``OPTIONAI_LOG_LEVEL=DEBUG`` sets :attr:`log_level`.
    """

    model_config = SettingsConfigDict(
        env_prefix="OPTIONAI_",
        env_file=Path.home() / ".secrets" / ".env",
        extra="ignore",
    )

    app_environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    request_timeout_seconds: int = Field(default=30, ge=1)
    api_url: str = "http://localhost:8000"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    technical_data_provider: Literal["direct", "mcp", "raw_mcp"] = "direct"
    mcp_url: str = "http://localhost:8001/mcp"
    mcp_port: int = Field(default=8001, ge=1, le=65535)
    options_risk_free_rate: float = Field(default=0.04, ge=0, le=1)
    llm_provider: Literal["openai", "google", "ollama"] = "google"
    # Optional per-agent overrides; empty values fall back to global settings.
    technical_llm_provider: Literal["openai", "google"] | None = None
    technical_llm_model: str | None = None
    market_context_llm_provider: Literal["openai", "google"] | None = None
    market_context_llm_model: str | None = None
    ticker_news_llm_provider: Literal["openai", "google"] | None = None
    ticker_news_llm_model: str | None = None
    options_llm_provider: Literal["openai", "google"] | None = None
    options_llm_model: str | None = None
    recommendation_llm_provider: Literal["openai", "google"] | None = None
    recommendation_llm_model: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "OPENAI_AI_KEY"),
    )
    google_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    openai_model: str = Field(default="gpt-5-nano", min_length=1)
    google_model: str = Field(default="gemini-3.1-flash-lite", min_length=1)
    openai_reasoning_effort: Literal["minimal", "low", "medium", "high"] = "minimal"
    google_thinking_level: Literal["minimal", "low", "medium", "high"] = "minimal"
    google_thinking_budget: int | None = Field(default=None, ge=0)
    llm_max_output_tokens: int = Field(default=6000, ge=256)


settings = Settings()
