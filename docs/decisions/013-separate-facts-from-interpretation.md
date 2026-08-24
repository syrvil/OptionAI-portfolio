# ADR-013: Keep calculated facts separate from LLM interpretation

## Decision

The application owns the validated price and indicator data. The Technical
Analysis Agent returns only a `TechnicalAnalysisInterpretation` containing
plain-language interpretation, evidence, risks, and invalidation conditions.
Python assembles the final `TechnicalAnalysisReport` from both parts.

## Rationale

Indicator values are deterministic business data and should not be regenerated
by an LLM. Separating them prevents accidental changes or omissions, makes the
report easier to inspect, and keeps provider-specific model behavior out of the
data layer.

## Consequences

The prompt and tests validate interpretation fields rather than duplicated
indicator fields. Future LangGraph nodes can calculate indicators, generate an
interpretation, and assemble a report as separate steps.
