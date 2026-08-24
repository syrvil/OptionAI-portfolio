# ADR-036: Use specialized service images for Compose

## Decision

Docker Compose will build separate runtime images for the API, Streamlit, and
MCP services. A direct Dockerfile build will continue to support one shared
runtime image for simple local use.

## Context

The first shared runtime image was approximately 892 MB. It was easy to use,
but every service carried dependencies required by other services. The
specialized images measured approximately 611 MB for API, 564 MB for Streamlit,
and 359 MB for MCP after removing unnecessary options dependencies.

## Rationale

The API runs the complete StateGraph workflow and therefore needs the backend,
LLM, news, and options dependencies. Streamlit mainly renders responses and
calls FastAPI. MCP provides deterministic price-history data. Giving each
service an appropriate dependency set reduces unnecessary image content and
creates clearer boundaries for later Cloud Run deployment.

The images still share common Python and data libraries. Zero overlap is not a
goal; Docker registries can reuse identical layers, and removing all shared
code would make the system harder to understand.

## Consequences

- Compose has more than one image to build, inspect, and deploy.
- The non-Docker launcher and shared direct Docker build remain available.
- API, Streamlit, and MCP can be scaled or deployed independently later.
- Dependency changes must be tested against the service that imports them.
- Cloud storage and transfer costs must be measured with registry layer reuse,
  not by simply adding displayed image sizes.
