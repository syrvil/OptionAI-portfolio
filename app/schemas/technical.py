"""Sanitized examples of validated technical-analysis data contracts.

The production schema names and exact LLM fact contract are intentionally not
published in this portfolio edition.
"""

from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    """Validated input for a deterministic time-series calculation."""

    values: list[float] = Field(min_length=1)
    lookback: int = Field(gt=0)


class CalculationResult(BaseModel):
    """Result aligned with the supplied time series."""

    name: str
    values: list[float | None]


class AnalysisFacts(BaseModel):
    """Generic compact facts supplied to an LLM explanation agent."""

    current_state: str
    recent_changes: dict[str, float | None] = Field(default_factory=dict)
    supporting_metrics: dict[str, float | None] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
