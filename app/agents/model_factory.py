"""Create a configured provider through LangChain's common initializer."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.config.config import settings


def create_chat_model() -> BaseChatModel:
    """Create the configured chat model.

    Provider-specific options stay in this factory. Agent code depends on
    LangChain's common chat-model interface.
    """
    if settings.llm_provider == "openai":
        return init_chat_model(
            f"openai:{settings.openai_model}",
            api_key=settings.openai_api_key,
            timeout=settings.request_timeout_seconds,
            reasoning_effort=settings.openai_reasoning_effort,
            max_completion_tokens=settings.llm_max_output_tokens,
        )
    if settings.llm_provider == "google":
        return init_chat_model(
            f"google_genai:{settings.google_model}",
            google_api_key=settings.google_api_key,
            timeout=settings.request_timeout_seconds,
            max_tokens=settings.llm_max_output_tokens,
            thinking_level=settings.google_thinking_level,
            thinking_budget=settings.google_thinking_budget,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
