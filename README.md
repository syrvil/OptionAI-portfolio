# OptionAI — AI engineering portfolio

OptionAI is an AI-assisted, multi-agent decision-support system for options
analysis. It combines deterministic market calculations with structured LLM
interpretation while keeping the user in control. It does not place trades or
make autonomous investment decisions.

This repository is a curated, non-runnable portfolio edition. It demonstrates
architecture, engineering practices, infrastructure patterns, and selected
implementation examples. Production business logic, complete strategy rules,
private prompts, and some integration code remain in the private repository.

## Why this project exists

The project has three connected goals:

1. **Build something useful.** OptionAI is based on my personal experiences as
   an investor and trader. It formalizes a decision-making process learned
   through trial and error, with the goal of making risks and uncertainty more
   visible.
2. **Apply my Data Science studies.** The project turns learning from my
   Master's studies—especially AI/ML, data processing, and software
   development practices—into a substantial engineering project.
3. **Learn modern AI engineering.** The project provides a practical setting
   for developing skills in multi-agent systems, LLM-provider abstraction,
   workflow orchestration, API design, distributed services, cloud deployment,
   and disciplined AI-assisted software development.

## What this project demonstrates

### Multi-agent AI engineering

- specialized Technical Analysis, Market Context, Ticker News, Options, and
  Recommendation agent boundaries;
- deterministic StateGraph supervision of the agent workflow;
- parallel analysis branches and progressive, human-in-the-loop continuation;
- schema-guided structured LLM responses;
- provider-neutral model integration through a model factory;
- support for hosted LLM providers through a provider-neutral model factory,
  with a boundary for future local models;
- explicit cache, model, token-usage, and request-duration metadata.

### Software architecture

```text
Streamlit UI
     ↓
FastAPI application boundary
     ↓
StateGraph supervisor
     ├── Technical Analysis Agent
     ├── Market Context Agent
     ├── Ticker News Agent
     ├── Options Analysis Agent
     └── Recommendation Agent
             ↓
       Provider-neutral model factory
```

The design separates responsibilities deliberately:

- deterministic Python code calculates validated facts and decision outcomes;
- agents interpret, classify, summarize, and explain those facts;
- Pydantic schemas define service and API contracts;
- tools isolate deterministic calculations and provider orchestration;
- services isolate external providers and cache/storage behavior;
- MCP is an optional provider boundary, not the workflow supervisor.

The included prompts and schemas are sanitized examples. They demonstrate
structured outputs, evidence and risk reporting, and the separation between
validated facts and LLM explanation. The production calculations, indicator
combinations, options-selection rules, recommendation thresholds, exact
LLM-facing fact contract, and production prompt wording remain private.

### Platform and delivery engineering

- Docker and Docker Compose service boundaries;
- specialized API, Streamlit, and MCP images;
- GitHub Actions quality gates and container builds;
- Ruff, MyPy, pytest, Bandit, Gitleaks, pre-commit, and Grype;
- Google Cloud Run deployment design;
- Artifact Registry image publication;
- Cloud Storage durable cache and raw-data persistence;
- Secret Manager for managed secrets;
- Workload Identity Federation instead of long-lived cloud keys;
- separate runtime service accounts and private service-to-service calls.

## Cloud architecture example

```text
Public Streamlit
       │ audience-specific identity token
       ▼
Private FastAPI API
       │ audience-specific identity token
       ▼
Private MCP service
       │
       ▼
Google Cloud Storage
```

Only Streamlit is public. GitHub Actions authenticates to Google Cloud through
Workload Identity Federation. Cloud Run uses separate runtime identities for
Streamlit, API, and MCP. The full deployment walkthrough is intentionally
sanitized, but the architecture and security boundaries are documented in
[`docs/architecture.md`](docs/architecture.md) and
[`docs/phases/phase-05-cloud-deployment.md`](docs/phases/phase-05-cloud-deployment.md).

## Application preview

![OptionAI Streamlit application](assets/OptionAI.png)

## Selected documentation

- [Architecture overview](docs/architecture.md)
- [Cache flow](docs/cache_flow.md)
- [StateGraph design](docs/stategraph_design.md)
- [Selected architecture decisions](docs/decisions/README.md)
- [Development and quality principles](docs/development_guidelines.md)
- [Project roadmap](docs/roadmap.md)

The documentation is selected to show engineering reasoning. Private learning
journals, detailed production implementation logs, personal investment notes,
and strategy-specific decisions are intentionally omitted.

## Public-edition scope

The public files are representative examples, not a complete product release.
Some modules, schemas, prompts, dependencies, and service implementations have
been removed or sanitized to protect the product's business logic. Therefore,
the Docker, Compose, CI, and Cloud Run files should be read as engineering
artifacts and design examples, not as a promise that this directory can be run
independently.

The complete private implementation can be demonstrated or shared selectively
during a serious hiring process. It contains the complete business logic,
production prompts, strategy rules, full API contracts, and live deployment
configuration.

## AI-assisted development

The project was developed with OpenAI Codex assistance. I personally defined
the architecture, deterministic business rules, testing strategy,
documentation, and acceptance criteria, and reviewed and validated generated
changes. Repository instructions, an architecture document, ADRs, a product
backlog, and implementation records were used to keep AI assistance disciplined
and reviewable.

## Technology areas

Python · FastAPI · Streamlit · LangChain · LangGraph · Pydantic · MCP/FastMCP ·
pandas · yfinance · Docker · Docker Compose · GitHub Actions · Google Cloud
Run · Artifact Registry · Cloud Storage · Secret Manager · pytest · Ruff ·
MyPy · Bandit · Gitleaks · Grype

## License

Copyright © 2026. All rights reserved.

This repository is published for portfolio and evaluation purposes. No
permission is granted to copy, modify, redistribute, or use the code
commercially without written permission.
