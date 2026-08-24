"""Sanitized example of a schema-guided domain agent."""

from typing import Any

from app.schemas.technical import AnalysisFacts


class TechnicalAnalysisAgent:
    """Interpret compact deterministic facts without calculating new metrics."""

    def __init__(self, model: Any | None = None) -> None:
        self.model = model

    def analyze(self, facts: AnalysisFacts) -> dict[str, object]:
        """Return a structured interpretation from a prepared facts object."""
        if self.model is None:
            return {"interpretation": "model invocation omitted from portfolio copy"}
        result = self.model.invoke({"facts": facts.model_dump()})
        return {"interpretation": result}
