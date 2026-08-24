"""Validated data schemas for market prices."""

from datetime import date, datetime
from math import isfinite
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PriceHistoryRequest(BaseModel):
    """Validated request for historical daily price data."""

    ticker: str = Field(min_length=1)
    start_date: date
    end_date: date
    interval: Literal["1d"] = "1d"

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        """Normalize ticker symbols before they reach a data provider."""
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("ticker must not be empty")
        return normalized

    @model_validator(mode="after")
    def validate_date_range(self) -> "PriceHistoryRequest":
        """Ensure the requested range has a positive duration."""
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PriceBar(BaseModel):
    """Validated OHLCV data for one market timestamp."""

    timestamp: datetime
    open: float = Field(ge=0)
    high: float = Field(ge=0)
    low: float = Field(ge=0)
    close: float = Field(ge=0)
    volume: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_values(self) -> "PriceBar":
        """Ensure prices are finite and OHLC values are internally consistent."""
        prices = (self.open, self.high, self.low, self.close)
        if not all(isfinite(price) for price in prices):
            raise ValueError("OHLC prices must be finite values")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be at least every other OHLC price")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be no greater than every other OHLC price")
        return self


class PriceHistory(BaseModel):
    """Validated historical price series returned by a market-data service."""

    ticker: str
    bars: list[PriceBar] = Field(min_length=1)
    provider: str = "yfinance"
    retrieved_at: datetime
    cache_status: Literal["hit", "miss"] | None = None
