# Phase 4b — Service-specific Docker images

## Goal

Reduce cloud image transfer and startup overhead by giving the API, Streamlit,
and MCP services only the runtime dependencies they need.

## Starting point

The v0.15 Compose deployment uses one shared runtime image. This is simple and
works locally, but it includes UI dependencies such as Streamlit and PyArrow in
services that do not need them.

The parameterized Dockerfile preserves this shared-image option. A direct
`docker build` uses the default `requirements-runtime.txt`, while Compose
overrides `RUNTIME_REQUIREMENTS` for each service and builds specialized
images. Both workflows remain supported.

## Target structure

```text
optionai-api       → FastAPI, StateGraph, agents, data services, LLM clients
optionai-streamlit → Streamlit UI and presentation dependencies
optionai-mcp       → MCP server and deterministic market-data services
```

All images must continue to use the same schemas, service interfaces,
environment-variable names, cache policies, and deterministic workflow rules.

## Dependency map

The API needs the complete analysis runtime: FastAPI, StateGraph, agents, data
services, LLM clients, and the MCP client library. The Streamlit image needs the
UI and API-client dependencies, including Streamlit and its presentation
stack. The FastMCP image needs the MCP server, configuration, schemas, and
market-data services. The current FastMCP server also imports the technical
analysis runner, so its image cannot yet be reduced to only a raw data client
without a code-boundary change. The raw MCP server has a smaller logical
boundary, but it still shares the application package and dependency file until
the specialized images are implemented.

## Work sequence

1. Measure the shared-image baseline.
2. Map imports and runtime dependencies by service.
3. Create separate runtime dependency files and image definitions.
4. Update Compose to select the specialized images.
5. Compare image sizes and verify all provider modes and cache behavior.
6. Document the final boundaries before cloud deployment planning.

## Constraints

The non-Docker launcher remains unchanged. This phase optimizes packaging; it
does not split the StateGraph or introduce service-specific business logic.
Cloud-managed storage and deployment configuration remain Phase 5 concerns.

The MCP dependency set excludes `vollib` because the current MCP tools provide
technical price data only. `vollib` and its SciPy dependency remain in the API
and Streamlit images for options analysis.

The resulting local image measurements were approximately 611 MB for API,
892 MB for Streamlit, and 469 MB for MCP after removing `vollib`. The MCP raw
provider workflow, including continuation and cache reuse, was verified with
the specialized images.

The minimal Streamlit image reduced the image from approximately 892 MB to
564 MB. Live Compose testing then confirmed MCP startup, initial analysis, and
continuation analysis with the reduced UI dependency set.

The remaining optimization opportunity is to investigate Streamlit separately.
The UI module still
imports several backend runners and agents at module load time, even though
the normal workflow calls FastAPI. Those imports may be removable or lazily
loaded, but the change must preserve historical review and all rendered
reports.

The API and MCP image audits were also completed. The API retains most analysis
dependencies because it owns the complete workflow. MCP has the smaller
raw-data boundary than the embedded FastMCP technical-analysis server, and the
two server modes now share the aligned provider capability.

Phase 4b is complete. The optimized images preserve the same service
interfaces, provider modes, cache volumes, and workflow behavior while
reducing unnecessary dependencies. Cloud deployment uses these service
boundaries as its starting point.

FastMCP and raw MCP now expose the same `get_price_history` tool. Live FastMCP
testing confirmed initial and continuation analysis with the aligned interface;
the API/StateGraph remains responsible for the complete Technical Analysis
workflow.

The API audit found no safe large dependency to remove while retaining the
complete configurable workflow. Options analysis requires `vollib` and SciPy,
news requires `ddgs` and yfinance, and both configured LLM providers must
remain available. MCP client dependencies are also needed when an MCP provider
mode is selected. Further API reduction would require separate provider- or
workflow-specific images, which is deferred.

The API dependency audit and FastMCP/raw MCP tool alignment are complete. Both
expose the provider capability used by the workflow, `get_price_history`. The
extra FastMCP convenience tool for running complete Technical Analysis is not
part of the authoritative API workflow.

The MCP audit also found that `app/services/__init__.py` eagerly imported the
options-data service. It is now side-effect-free, matching the tools and agents
package boundaries. The aligned `requirements-mcp.txt` serves both MCP server
modes because they expose the same provider capability.
