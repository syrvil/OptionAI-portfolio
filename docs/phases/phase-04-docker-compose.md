# Phase 4 — Docker Compose local deployment

## Goal

Run the interfaces as separate local containers while retaining one shared
application core and reproducible configuration.

## Initial services

```text
streamlit     → api → StateGraph and domain services
mcp-client    → mcp-server → shared tools and services
```

The first Compose setup should contain `streamlit`, `api`, and `mcp-server`.
Add a worker, database, queue, or external cache only when a verified requirement
exists.

The first services share one runtime image built from `requirements-runtime.txt`.
Development and test packages from `requirements.txt` are not copied into the
container dependency set. This keeps the initial service boundary simple while
making the image smaller than a development image.

The provider is selected through environment variables. `mcp` uses the
embedded FastMCP server, `raw_mcp` uses the low-level MCP server, and `direct`
keeps the API on the direct provider while the MCP service remains available
for comparison. Compose uses service names for internal URLs; the non-Docker
launcher continues to use localhost URLs.

## Design constraints

Containers must receive configuration through environment or managed secret
inputs. Persistent cache volumes must be explicit. Health checks must distinguish
service availability from provider availability. No API keys or local secrets
may be copied into images.

## Verification

Build images, start the Compose stack, exercise FastAPI and MCP health paths,
run a mocked analysis, verify service-to-service networking, inspect logs, and
confirm cache-volume behavior after a restart.

## Migration result

Local development remains possible without containers. Compose becomes the
repeatable integration environment for the later cloud deployment.

Service-specific images are a later optimization. They may reduce cloud image
transfer and startup costs by keeping Streamlit/PyArrow out of API and MCP
images, but they are not required for the first local Compose milestone.
