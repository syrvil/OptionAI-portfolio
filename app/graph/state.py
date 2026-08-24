"""Sanitized StateGraph state example."""

from typing import TypedDict


class PortfolioState(TypedDict, total=False):
    """Generic state carried between workflow nodes."""

    asset: str
    start_date: object
    end_date: object
    scenario: str | None
    reports: dict[str, object]
    assessments: list[dict[str, object]]
    deterministic_outcome: str | None
    status: str
    warnings: list[str]
    error: str | None
