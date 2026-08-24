"""Tests for market-data schemas and provider conversion."""

import os
from datetime import date, datetime, timedelta, tzinfo
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from app.schemas.market_data import PriceBar, PriceHistoryRequest
from app.services import market_data
from app.services.market_data import MarketDataError, YFinancePriceHistoryService
from app.services.raw_data import RawMarketDataStore


def test_price_history_request_normalizes_ticker() -> None:
    """Ticker symbols are normalized before provider calls."""
    request = PriceHistoryRequest(
        ticker="  aapl ",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 10),
    )

    assert request.ticker == "AAPL"
    assert request.interval == "1d"


def test_price_history_request_rejects_invalid_date_range() -> None:
    """The end date must follow the start date."""
    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        PriceHistoryRequest(
            ticker="AAPL",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 1, 1),
        )


def test_price_bar_rejects_inconsistent_ohlc_values() -> None:
    """OHLC validation prevents impossible bars from entering the application."""
    with pytest.raises(ValidationError, match="high must be at least"):
        PriceBar(
            timestamp="2026-01-02T00:00:00Z",
            open=105,
            high=100,
            low=95,
            close=98,
            volume=1000,
        )


def test_yfinance_service_transforms_provider_rows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The service returns typed bars and preserves provider metadata."""
    frame = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 100.0],
            "Close": [104.0, 105.0],
            "Volume": [1000, 1200],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-05"]),
    )
    monkeypatch.setattr(market_data.yf, "download", lambda **_: frame)
    request = PriceHistoryRequest(
        ticker="aapl",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 10),
    )

    result = YFinancePriceHistoryService(
        RawMarketDataStore(tmp_path), cache_directory=tmp_path / "cache"
    ).get_history(request)

    assert result.ticker == "AAPL"
    assert result.provider == "yfinance"
    assert len(result.bars) == 2
    assert result.bars[0].close == 104.0
    assert result.bars[1].volume == 1200
    assert len(list(tmp_path.glob("*.csv"))) == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_yfinance_service_rejects_incomplete_latest_ohlc_row(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An incomplete latest provider row stops the workflow."""
    frame = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 100.0],
            "Close": [104.0, float("nan")],
            "Volume": [1000, float("nan")],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-05"]),
    )
    monkeypatch.setattr(market_data.yf, "download", lambda **_: frame)

    with pytest.raises(MarketDataError, match="Latest market-data row.*2026-01-05"):
        YFinancePriceHistoryService(
            RawMarketDataStore(tmp_path), cache_directory=tmp_path / "cache"
        ).get_history(
            PriceHistoryRequest(
                ticker="AAPL",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 10),
            )
        )


def test_yfinance_service_rejects_empty_provider_response(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An empty provider response becomes a clear domain error."""
    monkeypatch.setattr(market_data.yf, "download", lambda **_: pd.DataFrame())
    request = PriceHistoryRequest(
        ticker="AAPL",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 10),
    )

    with pytest.raises(MarketDataError, match="No market data returned"):
        YFinancePriceHistoryService(
            RawMarketDataStore(tmp_path / "raw"), cache_directory=tmp_path / "cache"
        ).get_history(request)


def test_yfinance_service_reuses_fresh_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A repeated request reads the cache instead of calling the provider."""
    frame = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [104.0],
            "Volume": [1000],
        },
        index=pd.to_datetime(["2026-01-02"]),
    )
    calls = []
    monkeypatch.setattr(
        market_data.yf, "download", lambda **_: calls.append(True) or frame
    )
    request = PriceHistoryRequest(
        ticker="AAPL", start_date="2026-01-01", end_date="2026-01-10"
    )
    service = YFinancePriceHistoryService(
        RawMarketDataStore(tmp_path / "raw"), cache_directory=tmp_path / "cache"
    )

    service.get_history(request)
    service.get_history(request)

    assert len(calls) == 1
    assert len(list((tmp_path / "cache").glob("*.csv"))) == 1


def test_current_end_date_refreshes_cache_after_current_day_ttl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A request ending on a trading day does not reuse a stale snapshot."""
    current_date = date(2026, 8, 21)  # Friday; keep the test independent of CI date.

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> "FixedDateTime":
            return cls(
                current_date.year,
                current_date.month,
                current_date.day,
                tzinfo=tz,
            )

    monkeypatch.setattr(market_data, "datetime", FixedDateTime)
    frame = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [104.0],
            "Volume": [1000],
        },
        index=pd.to_datetime([current_date - timedelta(days=1)]),
    )
    calls = []
    monkeypatch.setattr(
        market_data.yf, "download", lambda **_: calls.append(True) or frame
    )
    request = PriceHistoryRequest(
        ticker="AAPL",
        start_date=current_date - timedelta(days=365),
        end_date=current_date,
    )
    service = YFinancePriceHistoryService(
        RawMarketDataStore(tmp_path / "raw"), cache_directory=tmp_path / "cache"
    )
    service.get_history(request)
    cached_csv = next((tmp_path / "cache").glob("*.csv"))
    stale_time = (FixedDateTime.now() - timedelta(hours=2)).timestamp()
    os.utime(cached_csv, (stale_time, stale_time))

    service.get_history(request)

    assert len(calls) == 2
