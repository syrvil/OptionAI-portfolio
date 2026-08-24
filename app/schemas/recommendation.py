"""Sanitized examples of report-assessment schemas."""

from typing import Literal

from pydantic import BaseModel, Field

AssessmentSignal = Literal["supports", "neutral", "conflicts"]
DecisionOutcome = Literal["positive", "cautious", "deferred"]


class ReportAssessment(BaseModel):
    """One report's relationship to a user-selected scenario."""

    source: str
    signal: AssessmentSignal
    reason: str


class AssessmentFacts(BaseModel):
    """Validated facts supplied to a classification step."""

    scenario: str
    reports: list[str] = Field(min_length=1)


class ClassificationResult(BaseModel):
    """Structured model output; Python owns the final outcome rule."""

    assessments: list[ReportAssessment] = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class DecisionReport(BaseModel):
    """Sanitized final report shape."""

    scenario: str
    outcome: DecisionOutcome
    assessments: list[ReportAssessment] = Field(min_length=1)
    explanation: str
