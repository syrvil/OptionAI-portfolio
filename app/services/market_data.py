"""Market-data services backed by external providers."""

import json
import logging
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import cast

import pandas as pd  # type: ignore[import-untyped]
import yfinance as yf  # type: ignore[import-untyped]

from app.schemas.market_data import PriceBar, PriceHistory, PriceHistoryRequest
from app.services.raw_data import RawMarketDataStore

logger = logging.getLogger(__name__)


class MarketDataError(RuntimeError):
    """Raised when a market-data provider cannot return valid price data."""


class YFinancePriceHistoryService:
    """Retrieve and validate daily historical prices from Yahoo Finance."""

    def __init__(
        self,
        raw_data_store: RawMarketDataStore | None = None,
        cache_directory: Path = Path("data/cache"),
        cache_ttl: timedelta = timedelta(days=1),
        current_day_cache_ttl: timedelta = timedelta(hours=1),
    ) -> None:
        self.raw_data_store = raw_data_store or RawMarketDataStore(Path("data/raw"))
        self.cache_directory = cache_directory
        self.cache_ttl = cache_ttl
        self.current_day_cache_ttl = current_day_cache_ttl

    def get_history(
        self, request: PriceHistoryRequest, *, force_refresh: bool = False
    ) -> PriceHistory:
        """Retrieve history, refreshing only the current day when requested."""
        today = datetime.now(UTC).date()
        if request.start_date < today < request.end_date:
            historical = self._get_history_single(
                request.model_copy(update={"end_date": today}),
                force_refresh=force_refresh,
            )
            current = self._get_history_single(
                request.model_copy(update={"start_date": today}),
                force_refresh=force_refresh,
            )
            bars = {bar.timestamp: bar for bar in historical.bars}
            bars.update({bar.timestamp: bar for bar in current.bars})
            return historical.model_copy(
                update={"bars": sorted(bars.values(), key=lambda bar: bar.timestamp)}
            )
        return self._get_history_single(request, force_refresh=force_refresh)

    def _get_history_single(
        self, request: PriceHistoryRequest, *, force_refresh: bool = False
    ) -> PriceHistory:
        """Retrieve historical prices for a validated request.

        Args:
            request: Ticker and date range to retrieve.

        Returns:
            Validated price history ordered as returned by the provider.

        Raises:
            MarketDataError: If the provider fails, returns no data, or returns
                data without the required OHLCV columns.
        """
        today = datetime.now(UTC).date()
        current_day = request.end_date >= today and today.weekday() < 5
        cached_result = (
            None
            if force_refresh
            else self._read_cache(request, current_day=current_day)
        )
        frame = cached_result[0] if cached_result is not None else None
        retrieved_at = (
            cached_result[1] if cached_result is not None else datetime.now(UTC)
        )
        cache_hit = frame is not None
        if not cache_hit:
            try:
                frame = yf.download(
                    tickers=request.ticker,
                    start=request.start_date,
                    end=request.end_date,
                    interval=request.interval,
                    auto_adjust=False,
                    actions=False,
                    progress=False,
                    multi_level_index=False,
                )
            except Exception as exc:
                logger.exception("Market-data request failed for %s", request.ticker)
                raise MarketDataError(
                    f"Unable to retrieve market data for {request.ticker}"
                ) from exc

            self._write_cache(request, frame)

        if frame is None or frame.empty:
            raise MarketDataError(f"No market data returned for {request.ticker}")

        try:
            if not cache_hit:
                self.raw_data_store.save(
                    request.ticker,
                    frame,
                    {
                        "provider": "yfinance",
                        "ticker": request.ticker,
                        "start_date": request.start_date.isoformat(),
                        "end_date": request.end_date.isoformat(),
                        "interval": request.interval,
                        "retrieved_at": datetime.now(UTC).isoformat(),
                        "adjusted_prices": "false",
                    },
                )
        except (OSError, ValueError) as exc:
            raise MarketDataError(
                f"Unable to save raw market data for {request.ticker}"
            ) from exc

        normalized_frame = _normalize_columns(frame)
        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        if not required_columns.issubset(normalized_frame.columns):
            missing = sorted(required_columns - set(normalized_frame.columns))
            raise MarketDataError(
                f"Market data is missing columns: {', '.join(missing)}"
            )

        latest_row = normalized_frame.iloc[-1]
        if latest_row[["Open", "High", "Low", "Close"]].isna().any():
            latest_timestamp = _timestamp(normalized_frame.index[-1])
            raise MarketDataError(
                f"Latest market-data row for {request.ticker} is incomplete "
                f"({latest_timestamp.date().isoformat()}); please retry later"
            )
        normalized_frame = normalized_frame.dropna(
            subset=["Open", "High", "Low", "Close"]
        )
        if normalized_frame.empty:
            raise MarketDataError(
                f"Market data contains no valid price bars for {request.ticker}"
            )

        bars = [
            _price_bar(timestamp, row) for timestamp, row in normalized_frame.iterrows()
        ]
        return PriceHistory(
            ticker=request.ticker,
            bars=bars,
            retrieved_at=retrieved_at,
            cache_status="hit" if cache_hit else "miss",
        )

    def _cache_paths(self, request: PriceHistoryRequest) -> tuple[Path, Path]:
        """Return deterministic cache paths for one provider request."""
        stem = (
            f"{request.ticker}_{request.start_date}_{request.end_date}_"
            f"{request.interval}"
        )
        return (
            self.cache_directory / f"{stem}.csv",
            self.cache_directory / f"{stem}.json",
        )

    def _read_cache(
        self, request: PriceHistoryRequest, *, current_day: bool = False
    ) -> tuple[pd.DataFrame, datetime] | None:
        """Read a fresh cached provider table, if one exists."""
        csv_path, metadata_path = self._cache_paths(request)
        if not csv_path.exists() or not metadata_path.exists():
            return None
        age = datetime.now().timestamp() - csv_path.stat().st_mtime
        ttl = self.current_day_cache_ttl if current_day else self.cache_ttl
        if age > ttl.total_seconds():
            return None
        try:
            frame = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(metadata["cached_at"])
            return frame, cached_at
        except (OSError, KeyError, TypeError, ValueError, pd.errors.ParserError):
            logger.warning("Ignoring unreadable market-data cache %s", csv_path)
            return None

    def _write_cache(self, request: PriceHistoryRequest, frame: pd.DataFrame) -> None:
        """Write a provider table and request metadata to the local cache."""
        if frame is None or frame.empty:
            return
        csv_path, metadata_path = self._cache_paths(request)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        frame.to_csv(csv_path)
        metadata_path.write_text(
            json.dumps(
                {
                    "provider": "yfinance",
                    "ticker": request.ticker,
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                    "interval": request.interval,
                    "cached_at": datetime.now(UTC).isoformat(),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Flatten provider columns when a DataFrame has a ticker level."""
    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        frame.columns = frame.columns.get_level_values(0)
    return frame


def _price_bar(timestamp: object, row: Mapping[str, object]) -> PriceBar:
    """Convert one provider row into a validated price bar."""
    volume = row["Volume"]
    volume_value = None if pd.isna(volume) else int(float(str(volume)))
    return PriceBar(
        timestamp=_timestamp(timestamp),
        open=float(str(row["Open"])),
        high=float(str(row["High"])),
        low=float(str(row["Low"])),
        close=float(str(row["Close"])),
        volume=volume_value,
    )


def _timestamp(value: object) -> datetime:
    """Convert a provider timestamp to a Python datetime."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return cast(datetime, pd.Timestamp(value).to_pydatetime())
