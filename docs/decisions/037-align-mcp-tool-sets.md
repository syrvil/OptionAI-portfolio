# ADR-037: Align FastMCP and raw MCP tool sets

## Decision

FastMCP and raw MCP will expose the same provider capability:
`get_price_history`. Complete Technical Analysis remains an API/StateGraph
responsibility.

## Context

The original FastMCP demonstration also exposed
`run_technical_analysis_tool`, while the raw MCP server exposed only
`get_price_history`. This made the providers difficult to compare and loaded
technical-analysis, LLM, and options dependencies into the FastMCP image.

## Rationale

MCP is a provider interface in this architecture, not a second workflow
supervisor. The API receives price history through either direct, FastMCP, or
raw MCP mode, then calculates indicators and runs the Technical Analysis Agent.
Keeping both MCP implementations equivalent makes provider substitution easier
to test and keeps deterministic workflow authority in FastAPI/StateGraph.

## Consequences

- FastMCP and raw MCP have the same tool name, input shape, and output schema.
- The MCP images can use the minimal market-data dependency set.
- External MCP clients cannot request complete Technical Analysis through the
  MCP server; they must use the API for that workflow.
- Adding further MCP tools requires an explicit architecture decision and
  matching behavior in both server implementations if parity is intended.
