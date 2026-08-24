"""Sanitized example of the technical-analysis orchestration boundary."""

from collections.abc import Callable

from app.schemas.market_data import PriceHistory, PriceHistoryRequest
from app.schemas.technical import AnalysisFacts
from app.tools.technical_data import build_analysis_facts


def run_technical_analysis_example(
    request: PriceHistoryRequest,
    *,
    price_history_provider: Callable[[PriceHistoryRequest], PriceHistory],
    interpret: Callable[[AnalysisFacts], object],
) -> object:
    """Prepare deterministic facts, then pass them to an interpretation agent.

    The production runner also selects direct, FastMCP, or raw MCP providers.
    Those provider details and the production report contract are omitted here.
    """
    facts = build_analysis_facts(
        request,
        price_history_provider=price_history_provider,
    )
    return interpret(facts)
