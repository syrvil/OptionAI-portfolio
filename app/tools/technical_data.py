"""Sanitized example of a deterministic technical-data tool.

The production implementation calculates several standard indicators. Their
exact names, periods, and LLM-facing fields are intentionally generalized here.
"""

from collections.abc import Callable

from app.schemas.market_data import PriceHistory, PriceHistoryRequest
from app.schemas.technical import AnalysisFacts, CalculationRequest, CalculationResult


def build_analysis_facts(
    request: PriceHistoryRequest,
    *,
    price_history_provider: Callable[[PriceHistoryRequest], PriceHistory],
) -> AnalysisFacts:
    """Fetch validated history and prepare compact facts for an agent.

    Numerical calculations stay in deterministic Python code. The LLM receives
    the resulting compact facts, not the complete plotting/time-series data.
    """
    history = price_history_provider(request)
    values = [bar.close for bar in history.bars]
    result = _illustrative_calculation(values)
    return AnalysisFacts(
        current_state="validated time-series facts",
        recent_changes={"recent": _latest(result)},
        supporting_metrics={"sample_size": float(len(values))},
        limitations=[],
    )


def _illustrative_calculation(values: list[float]) -> CalculationResult:
    """Illustrate a typed deterministic calculation without production details."""
    request = CalculationRequest(values=values, lookback=min(5, len(values)))
    return CalculationResult(name="illustrative_metric", values=[None] * len(request.values))


def _latest(result: CalculationResult) -> float | None:
    """Return the latest available value from an aligned result."""
    return next((value for value in reversed(result.values) if value is not None), None)
