"""Sanitized examples of progressive analysis API schemas."""

from datetime import date

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Initial request accepted by the API boundary."""

    asset: str = Field(min_length=1)
    start_date: date
    end_date: date


class AnalysisResponse(BaseModel):
    """Initial reports and workflow status returned to the UI."""

    asset: str
    status: str
    reports: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ContinuationRequest(BaseModel):
    """Second request after the user selects a scenario."""

    asset: str = Field(min_length=1)
    scenario: str = Field(min_length=1)
    reports: list[dict[str, object]] = Field(min_length=1)
