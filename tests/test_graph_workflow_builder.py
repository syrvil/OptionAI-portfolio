"""Tests for constructing and invoking the synchronous StateGraph."""

import asyncio
from datetime import date
from typing import Any, cast

import pytest

from app.graph.workflow import (
    build_analysis_graph,
    invoke_analysis_graph_async,
    run_context_and_news_parallel,
)
from app.schemas.market_context import MarketContextReport
from app.schemas.technical_analysis_report import TechnicalAnalysisReport


def test_graph_builder_runs_technical_only_path(monkeypatch) -> None:
    report = cast(TechnicalAnalysisReport, object())
    market_report = cast(MarketContextReport, object())
    news_report = cast(object, object())
    monkeypatch.setattr(
        "app.graph.nodes.run_technical_analysis", lambda _request: report
    )
    graph = build_analysis_graph(
        lambda _report, _strategy: cast(object, None),
        lambda _date: market_report,
        lambda _ticker, _date: news_report,
    )

    result = graph.invoke(
        {
            "ticker": "AAPL",
            "start_date": date(2025, 1, 1),
            "end_date": date(2026, 1, 1),
            "options_strategy": None,
        }
    )

    assert result["status"] == "awaiting_strategy"
    assert result["technical_analysis_report"] is report
    assert result["market_context_report"] is market_report
    assert result["news_report"] is news_report
    assert result.get("options_report") is None


def test_graph_builder_supports_async_invocation(monkeypatch) -> None:
    class FakeAsyncGraph:
        async def ainvoke(self, state):
            return {**state, "status": "awaiting_strategy"}

    result = asyncio.run(
        invoke_analysis_graph_async(
            cast(Any, FakeAsyncGraph()),
            {
                "ticker": "AAPL",
                "start_date": date(2025, 1, 1),
                "end_date": date(2026, 1, 1),
                "options_strategy": None,
            },
        )
    )

    assert result["status"] == "awaiting_strategy"


def test_context_and_news_branches_run_concurrently() -> None:
    events: list[str] = []
    market_report = cast(MarketContextReport, object())
    news_report = cast(object, object())

    async def market_runner(_date):
        events.append("market-start")
        await asyncio.sleep(0)
        events.append("market-end")
        return market_report

    async def news_runner(_ticker, _date):
        events.append("news-start")
        await asyncio.sleep(0)
        events.append("news-end")
        return news_report

    result = asyncio.run(
        run_context_and_news_parallel(
            {
                "ticker": "AAPL",
                "end_date": date(2026, 8, 19),
            },
            market_context_runner=market_runner,
            news_runner=news_runner,
        )
    )

    assert events[:2] == ["market-start", "news-start"]
    assert result["market_context_report"] is market_report
    assert result["news_report"] is news_report


def test_parallel_branches_report_market_context_failure() -> None:
    async def market_runner(_date):
        raise ValueError("provider unavailable")

    async def news_runner(_ticker, _date):
        return cast(object, object())

    result = asyncio.run(
        run_context_and_news_parallel(
            {"ticker": "AAPL", "end_date": date(2026, 8, 19)},
            market_context_runner=market_runner,
            news_runner=news_runner,
        )
    )

    assert result.get("market_context_report") is None
    assert result["news_report"] is not None
    assert "Market Context unavailable" in result["warnings"][0]


def test_parallel_branches_timeout_is_reported() -> None:
    async def slow_market_runner(_date):
        await asyncio.sleep(1)
        return cast(MarketContextReport, object())

    async def slow_news_runner(_ticker, _date):
        await asyncio.sleep(1)
        return cast(object, object())

    with pytest.raises(RuntimeError, match="timed out"):
        asyncio.run(
            run_context_and_news_parallel(
                {"ticker": "AAPL", "end_date": date(2026, 8, 19)},
                market_context_runner=slow_market_runner,
                news_runner=slow_news_runner,
                timeout_seconds=0.01,
            )
        )


def test_parallel_context_and_news_match_sequential_results() -> None:
    market_report = cast(MarketContextReport, object())
    news_report = cast(object, object())

    def sync_market_runner(_date):
        return market_report

    def sync_news_runner(_ticker, _date):
        return news_report

    sequential = {
        "market_context_report": sync_market_runner(date(2026, 8, 19)),
        "news_report": sync_news_runner("AAPL", date(2026, 8, 19)),
    }

    async def async_market_runner(_date):
        return sync_market_runner(_date)

    async def async_news_runner(_ticker, _date):
        return sync_news_runner(_ticker, _date)

    parallel = asyncio.run(
        run_context_and_news_parallel(
            {"ticker": "AAPL", "end_date": date(2026, 8, 19)},
            market_context_runner=async_market_runner,
            news_runner=async_news_runner,
        )
    )

    assert parallel["market_context_report"] is sequential["market_context_report"]
    assert parallel["news_report"] is sequential["news_report"]
    assert parallel["warnings"] == []
