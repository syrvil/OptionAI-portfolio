# Phase 3 — FastMCP and raw MCP interfaces

## Goal

Expose a small, controlled set of validated tools through an independently
running MCP service, and make MCP useful inside the real workflow as an
optional data-provider path for Technical Analysis.

## Scope

- Verify the compatible MCP package before installation; this phase uses the
  embedded FastMCP implementation from `mcp==1.29.0` and does not install the
  separate `fastmcp` package.
- Add a separate FastMCP server adapter.
- Connect the Technical Analysis node to the MCP provider path.
- Verify the integrated functionality with live local evaluation.
- Reuse the existing schemas, services, and calculations.
- Build the lower-level MCP-library comparison only after FastMCP is usable.

## Transport

The user-facing integration uses HTTP transport. This avoids the observed
`stdio_client()` initialization hang and fits the planned Docker and cloud
deployment model, where services communicate through named network endpoints.
Stdio remains a separate comparison experiment only.

## Flow

```text
StateGraph → Technical Analysis node → configured provider

Direct mode: StateGraph → Technical Analysis → market-data service
MCP mode:    StateGraph → Technical Analysis → MCP client
                                      → HTTP FastMCP server → market-data service
```

The StateGraph still controls workflow order. MCP transports requested data; it
does not orchestrate the other agents or calculate recommendations. Provider
selection is configuration-driven, so the user runs one workflow rather than
choosing between duplicate UI buttons.

The local launcher reads these settings from the normal `OPTIONAI_` environment
configuration. Direct mode is the default:

```text
OPTIONAI_TECHNICAL_DATA_PROVIDER=direct
OPTIONAI_MCP_URL=http://localhost:8001/mcp
OPTIONAI_MCP_PORT=8001
```

The provider setting can expose three practical modes:

```text
OPTIONAI_TECHNICAL_DATA_PROVIDER=direct   # direct market-data service
OPTIONAI_TECHNICAL_DATA_PROVIDER=mcp      # MCP client → FastMCP server
OPTIONAI_TECHNICAL_DATA_PROVIDER=raw_mcp  # MCP client → raw MCP server
```

The `mcp` value selects the FastMCP server and `raw_mcp` selects the lower-level
MCP server. Both use the same client and tool schema.
```

### First tool: `get_price_history`

The first exposed capability is a read-only `get_price_history` tool. It uses
`PriceHistoryRequest` as its input schema and returns `PriceHistory`. The tool
accepts a ticker, start date, end date, and the fixed daily interval. Ticker
normalization, date validation, provider access, cache behavior, and incomplete
daily-bar checks remain in the existing schema and market-data service.

The MCP adapter only validates the tool call and delegates to that service; it
does not calculate indicators or create a second cache.

An optional later workflow tool may invoke the StateGraph, but individual tools
must not create parallel business logic.

## Design constraints

Tool inputs and outputs must be explicit and validated. Provider credentials and
filesystem paths remain server-side. MCP errors must identify validation,
provider, and incomplete-data failures without exposing secrets.

MCP exposure must not be confused with internal LLM tool binding. The
StateGraph remains responsible for internal workflow order, and agents will not
use LangChain `bind_tools()` for deterministic analysis tools. MCP clients may
choose among explicitly exposed read-only tools, but the server validates
requests and delegates to existing services.

## Verification

Test tool schemas, successful deterministic results, invalid requests, provider
failures, incomplete latest bars, and repeated calls. Compare MCP results with
the corresponding local service results.

## Raw MCP follow-up

The raw MCP implementation provides the same read-only tool with the lower-level MCP
library. It uses the existing HTTP client, schemas, deterministic service,
and Technical Analysis provider seam. The comparison must measure lifecycle,
tool registration, error handling, testing effort, and live behavior. It must
not duplicate market-data or indicator calculations.

The offline comparison confirms that both implementations expose the same
`get_price_history` name and required inputs. FastMCP reduces registration
boilerplate; the raw server makes the protocol handlers and schemas explicit.

## Migration result

FastAPI remains the application boundary, while the graph's Technical Analysis
provider can be configured as direct or MCP. The MCP server is a separate HTTP
service and can run in its own Docker container.
