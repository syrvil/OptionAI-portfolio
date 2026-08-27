"""Create a configured provider through LangChain's common initializer."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.config.config import settings


def resolve_agent_model(agent_name: str) -> tuple[str, str]:
    """Resolve an agent override, falling back to global settings."""
    prefix = agent_name.lower().replace(" ", "_")
    provider = getattr(settings, f"{prefix}_llm_provider", None)
    model = getattr(settings, f"{prefix}_llm_model", None)
    provider = provider or settings.llm_provider
    model = model or (
        settings.openai_model if provider == "openai" else settings.google_model
    )
    return provider, model


def create_chat_model(agent_name: str | None = None) -> BaseChatModel:
    """Create the configured chat model.

    Provider-specific options stay in this factory. Agent code depends on
    LangChain's common chat-model interface.
    """
    provider, model = resolve_agent_model(agent_name or "global")
    if provider == "openai":
        return init_chat_model(
            f"openai:{model}",
            api_key=settings.openai_api_key,
            timeout=settings.request_timeout_seconds,
            reasoning_effort=settings.openai_reasoning_effort,
            max_completion_tokens=settings.llm_max_output_tokens,
        )
    if provider == "google":
        return init_chat_model(
            f"google_genai:{model}",
            google_api_key=settings.google_api_key,
            timeout=settings.request_timeout_seconds,
            max_tokens=settings.llm_max_output_tokens,
            thinking_level=settings.google_thinking_level,
            thinking_budget=settings.google_thinking_budget,
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")
