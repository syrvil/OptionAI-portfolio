# Learning-oriented roadmap

This roadmap describes the planned technology-learning sequence after the v0.9
local MVP. It complements the active [product backlog](product_backlog.md) and
the historical [MVP roadmap](mvp_roadmap.md). The sequence is intentionally
incremental: each phase adds one important concept while preserving the shared
domain services and deterministic business rules.

## Guiding principles

- Keep one shared application core; interfaces are adapters around it.
- Add infrastructure only when it teaches a planned concept or solves a real
  operational problem.
- Keep Streamlit, FastAPI, and MCP from duplicating calculations or provider
  access.
- Verify each phase locally before moving to the next deployment boundary.
- Preserve the decision-support scope: no autonomous trading or execution.

## Sequence

```text
v0.9 local MVP
    ↓
v0.10 Phase 1: asynchronous StateGraph (complete)
    ↓
v0.11 Phase 2: FastAPI application boundary (complete)
    ↓
v0.12 FastMCP provider (complete)
    ↓
v0.13 raw MCP provider (complete)
    ↓
v0.14 API configuration and continuation improvements (complete)
    ↓
Phase 4: Docker Compose local deployment
    ↓
Phase 5: cloud deployment
```

## Phase 1 — Asynchronous StateGraph

Design document: [phase-01-async-stategraph.md](phases/phase-01-async-stategraph.md)

Run independent Market Context and Ticker News analyses concurrently after
technical analysis. Preserve deterministic routing, shared state validation,
cache behavior, and transparent failures. The synchronous graph remains the
reference path until the asynchronous implementation is verified.

Learning objectives:

- async Python and task coordination;
- concurrent StateGraph execution;
- cancellation and partial-failure handling;
- preserving deterministic aggregation after concurrent work.

## Phase 2 — FastAPI application boundary

Status: complete

Design document: [phase-02-fastapi.md](phases/phase-02-fastapi.md)

Expose the composed analysis workflow through FastAPI and migrate Streamlit to
call the HTTP API. The backend owns StateGraph execution; Streamlit becomes a
client. Define stable request, response, error, progress, and runtime-metadata
schemas before moving UI behavior.

Learning objectives:

- FastAPI routing and Pydantic API schemas;
- asynchronous request handling;
- client/server error and timeout behavior;
- API integration testing without provider calls.

## Phase 3 — FastMCP and MCP provider interfaces

Status: complete

Design document: [phase-03-mcp.md](phases/phase-03-mcp.md)

Use an HTTP FastMCP server as a configurable provider for Technical Analysis,
then implement a raw MCP-library server behind the same client interface. MCP
is a provider boundary used by the graph node, not a replacement for the
StateGraph or FastAPI workflow.

Learning objectives:

- MCP tool schemas and server lifecycle;
- controlled exposure of application capabilities;
- MCP client invocation and error handling;
- comparing FastMCP with the implemented raw MCP-library server.

## Phase 4 — Docker Compose local deployment

Status: complete

Design document: [phase-04-docker-compose.md](phases/phase-04-docker-compose.md)

The follow-up image-optimization design is documented in
[phase-04b-service-images.md](phases/phase-04b-service-images.md).

Phase 4b is also complete. It produced specialized API, Streamlit, and MCP
images, aligned the MCP provider tool sets, and verified the workflows and
cache volumes. Phase 5 can now use these service boundaries for cloud planning.

Run the interfaces as separate local services while sharing the same source
schemas and configured storage:

```text
Streamlit → FastAPI → StateGraph and domain services
MCP client → FastMCP → shared domain services
```

Begin with `streamlit`, `api`, and `mcp-server` containers. Add a worker or
external cache only if asynchronous execution or persistence requires it.

Learning objectives:

- container images and environment configuration;
- Compose networking, volumes, and service health;
- local service-to-service troubleshooting;
- keeping secrets outside images and source control.

## Phase 5 — Cloud deployment

Design document: [phase-05-cloud-deployment.md](phases/phase-05-cloud-deployment.md)

Deploy the reviewed containers to a managed cloud environment. Keep the first
deployment small: independently deploy the UI, API, and optional MCP service,
and replace container-local cache assumptions with an appropriate managed
storage strategy when needed.

Learning objectives:

- cloud service configuration and environment secrets;
- logs, health checks, and failure diagnosis;
- persistent storage and cache lifecycle;
- controlled CI/CD deployment and rollback.

## Completion rule

A phase is complete when its design document, implementation, offline tests,
local verification, and known limitations are documented. The authoritative
current architecture remains `docs/architecture.md`; phase documents record
the architecture at each learning step without creating competing sources of
truth.
