"""Sanitized StateGraph orchestration example."""

from collections.abc import Awaitable, Callable

from app.graph.state import PortfolioState

ReportRunner = Callable[[PortfolioState], PortfolioState]
AsyncReportRunner = Callable[[PortfolioState], Awaitable[PortfolioState]]


def run_initial_reports(
    state: PortfolioState,
    *,
    primary: ReportRunner,
    contextual: ReportRunner,
) -> PortfolioState:
    """Run the initial report stage before scenario selection."""
    state = primary(state)
    return contextual(state)


async def run_parallel_context(
    state: PortfolioState,
    *,
    first: AsyncReportRunner,
    second: AsyncReportRunner,
) -> PortfolioState:
    """Illustrate parallel independent report execution."""
    import asyncio

    results = await asyncio.gather(first(state), second(state), return_exceptions=True)
    merged = dict(state)
    for result in results:
        if isinstance(result, dict):
            merged.update(result)
        else:
            merged.setdefault("warnings", []).append("one contextual report failed")
    return merged


def continue_after_selection(
    state: PortfolioState,
    *,
    scenario_runner: ReportRunner,
    assessment_runner: ReportRunner,
) -> PortfolioState:
    """Run scenario-specific analysis and assessment after user selection."""
    if not state.get("scenario"):
        return {**state, "status": "awaiting_selection"}
    state = scenario_runner(state)
    return assessment_runner(state)
