# ADR-019: Use deterministic workflow supervision first

## Decision

The first multi-agent workflow uses a deterministic LangGraph `StateGraph` as
its supervisor. It owns sequencing, conditional routing, state validation,
completion, and failure handling. It is not a separate LLM agent.

An LLM supervisor or hybrid supervisor remains a future option. It may later
interpret user intent and select optional analyses such as news, market
context, fundamentals, or options analysis. Any such design must keep
deterministic safety and sequencing controls around financial workflows.

## Rationale

The current workflow is small and known: technical analysis followed by
optional options analysis. Fixed routing is easier to test, cheaper, and more
transparent than asking an LLM to choose every next step. A flexible supervisor
becomes more useful when the application has several optional domain agents and
varied user questions.

## Consequences

The current graph has no additional supervisor model cost and cannot silently
skip required steps. Future LLM or hybrid supervision will require explicit
tool or handoff boundaries, additional evaluation, and new backlog work.
