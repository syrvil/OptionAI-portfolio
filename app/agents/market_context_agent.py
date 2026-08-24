"""Provider-neutral Market Context Agent."""

import json
from pathlib import Path
from time import perf_counter
from typing import Protocol, cast

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.language_models import BaseChatModel

from app.agents.model_factory import create_chat_model
from app.config.config import settings
from app.prompts.market_context_prompt import MARKET_CONTEXT_PROMPT
from app.schemas.agent_runtime import AgentRuntimeMetadata
from app.schemas.market_context import (
    MarketContextInput,
    MarketContextInterpretation,
    MarketContextReport,
)
from app.services.cache import FileCache


class MarketContextChain(Protocol):
    """Minimal chain interface for offline injection."""

    def invoke(
        self, values: dict[str, str], **kwargs: object
    ) -> MarketContextInterpretation:
        """Return a validated market interpretation."""


class MarketContextAgent:
    """Interpret a compact, source-attributed market-news snapshot."""

    def __init__(
        self,
        model: BaseChatModel | None = None,
        chain: MarketContextChain | None = None,
        cache_directory: Path = Path("data/llm_cache"),
    ) -> None:
        if chain is None:
            structured_model = (model or create_chat_model()).with_structured_output(
                MarketContextInterpretation
            )
            chain = cast(MarketContextChain, MARKET_CONTEXT_PROMPT | structured_model)
        self.chain = chain
        self.cache = FileCache(cache_directory)
        self.last_usage: dict[str, object] = {}
        self.last_duration_seconds: float | None = None

    def analyze(
        self, analysis_input: MarketContextInput, *, force_refresh: bool = False
    ) -> MarketContextReport:
        """Generate a cached, structured market-context interpretation."""
        payload = json.dumps(analysis_input.model_dump(mode="json"), sort_keys=True)
        cache_payload = _cache_payload(analysis_input)
        cache_path = self.cache.path_for(
            settings.llm_provider,
            settings.google_model,
            "market-context",
            json.dumps(cache_payload, sort_keys=True),
        )
        cached = (
            None
            if force_refresh
            else self.cache.read(cache_path, analysis_input.analysis_date)
        )
        if cached is not None:
            interpretation = MarketContextInterpretation.model_validate(cached)
            self.last_usage = {}
            self.last_duration_seconds = 0.0
            return MarketContextReport(
                **analysis_input.model_dump(),
                interpretation=interpretation,
                runtime=AgentRuntimeMetadata(
                    provider=settings.llm_provider,
                    model=settings.google_model,
                    duration_seconds=0.0,
                    cache_status="hit",
                ),
            )
        usage_handler = UsageMetadataCallbackHandler()
        started = perf_counter()
        try:
            interpretation = self.chain.invoke(
                {"market_news": payload}, config={"callbacks": [usage_handler]}
            )
        except TypeError:
            interpretation = self.chain.invoke({"market_news": payload})
        self.last_duration_seconds = perf_counter() - started
        self.last_usage = dict(usage_handler.usage_metadata)
        self.cache.write(cache_path, interpretation.model_dump(mode="json"))
        return MarketContextReport(
            **analysis_input.model_dump(),
            interpretation=interpretation,
            runtime=AgentRuntimeMetadata(
                provider=settings.llm_provider,
                model=settings.google_model,
                duration_seconds=self.last_duration_seconds,
                token_usage=self.last_usage,
                cache_status="miss",
            ),
        )


def _cache_payload(analysis_input: MarketContextInput) -> dict[str, object]:
    """Remove retrieval timestamps so repeated identical news can be reused."""
    payload = analysis_input.model_dump(mode="json")
    news = payload["news"]
    if isinstance(news, dict):
        news.pop("collected_at", None)
        items = news.get("items")
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item.pop("retrieved_at", None)
    return payload
