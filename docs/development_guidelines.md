# Development Guidelines

## General Philosophy

The primary objective is to produce clean, maintainable, and production-quality software.

Prioritize:

* Simplicity over cleverness (KISS)
* Readability over brevity
* Maintainability over premature optimization
* Incremental development over large rewrites

Every feature should be independently testable and should improve the project without introducing unnecessary complexity.

## Feature Delivery Strategy

Prefer vertical slices over completing an entire architectural layer before it is
used. Each feature should connect the minimum number of layers needed to provide a
user-observable, testable outcome.

Avoid building general-purpose infrastructure, tools, or agents before an MVP slice
requires them. Extend the application incrementally from a working slice instead.

## Documentation Roles and Backlog Workflow

The documents have separate responsibilities:

* `project_vision.md` explains purpose and principles.
* `mvp_roadmap.md` describes broad release phases and order.
* `product_backlog.md` is the single source for current priorities and status.
* `mvp_specification.md` defines requirements for the current MVP.
* `architecture.md` describes the technical structure.
* `decisions/` records why important decisions were made.
* The private development journal records project history and lessons learned.
* The private implementation log records completed task slices, tests, live
  reviews, and implementation findings.

For implementation, consult the backlog, current MVP specification, and
architecture first. Do not duplicate requirements across documents. If a
decision changes behavior, update the specification and add an ADR. If release
order changes, update the roadmap and backlog together.

The human developer owns priorities and scope. The AI coding agent may clarify
or split backlog items, but must not silently reprioritize or expand them.

Before implementation starts, agree on the user-visible acceptance flow for the
slice, not only its internal classes or services. For each completed slice,
update the backlog status immediately and record the implementation, tests, and
review findings in the private implementation log. This prevents the backlog and
implementation history from drifting behind the code.

---

# Development Environment

## Operating System

Development targets Ubuntu Linux.

* Use POSIX-compliant paths (`src/utils/tools.py`)
* Never use Windows-specific paths or commands

---

## Python

* Python 3.12+
* Always use the active Conda environment
* Never rely on the system Python installation

---

## IDE

Recommended IDE:

* Visual Studio Code

Extensions are left to the developer's preference.

---

# Dependency Management

The project intentionally separates scientific dependencies from application dependencies.

## Conda

Conda manages:

* Python version
* Numerical libraries
* Scientific computing libraries
* Environment management

Configuration:

```text
environment.yml
```

---

## uv / pip

Application dependencies are managed using uv and pip.

Configuration:

```
requirements.txt
```

Examples include:

* LangChain
* LangGraph
* FastAPI
* Streamlit
* OpenAI
* Pydantic

Heavy scientific packages should remain in Conda whenever practical.

---

# Project Structure

```
app/

    agents/
    graph/
    services/
    tools/
    schemas/
    prompts/
    ui/
    config/

tests/

docs/

data/
```

Responsibilities:

**agents/**

Domain-specific AI reasoning.

**graph/**

LangGraph workflow.

**services/**

Communication with external APIs.

**tools/**

LLM-callable deterministic tools.

**schemas/**

Pydantic validation schemas for service, tool, and agent inputs and outputs.

**prompts/**

Prompt templates.

**ui/**

Streamlit user interface.

**config/**

Configuration and settings.

---

# Configuration Management

Configuration should be centralized.

Use:

```text
config.py
```

Configuration values should be loaded using:

* Pydantic BaseSettings
* Environment variables

All configurable values—including API keys, model names, endpoints, feature flags, and runtime parameters—must be managed through config.py using Pydantic BaseSettings. Application code should never access environment variables directly. Use the centralized Settings object from config.py for all configuration values.

---

## Secrets

Secrets must never be committed to Git.

Use:

```text
.env
```

The actual `.env` file should remain **outside the project workspace**.

Provide:

```text
.env.example
```

inside the repository.

Example values should use placeholders only.

Never hardcode:

* API keys
* passwords
* tokens
* secrets

---

# Security Checks

Security checks should provide fast local feedback and independent CI verification.

* Bandit scans Python code for common security issues.
* Gitleaks scans staged changes for accidentally committed secrets.
* GitHub push protection provides a server-side secret-leak safeguard where enabled.
* Dependabot monitors dependency manifests and reports known vulnerable versions.
* Grype scans built Docker images for known OS and library vulnerabilities.

Bandit and Gitleaks run through pre-commit for local feedback. Gitleaks is a
system executable (installed separately from the Python dependencies), and the
local hook scans the staged changes with `gitleaks git --pre-commit --staged`.
GitHub Actions runs the repository checks and container scans in CI. Run the
same checks locally before pushing to receive faster feedback and keep the
development workflow reproducible.

---

# Code Style

## Plain Language

Documentation, names, comments, and user-facing messages should use the
simplest accurate wording. Introduce a technical term only when it adds useful
precision, and explain it at first use. Prefer “expected input and output” to
“contract,” “coordinate the steps” to “orchestrate,” and “where the data came
from” to “provenance” when those simpler phrases are sufficient.

Before adding a new abstraction or technical term, ask whether a short
function, clear name, or direct explanation would communicate the idea better.
The code should favor the same principle: explicit, readable logic over clever
indirection.

### Project terminology

* **Schema:** a typed description used to validate data.
* **Service:** code that talks to an external system or provider.
* **Tool:** a focused operation that an agent may call.
* **Agent:** an LLM-based component that explains or coordinates; it does not
  replace deterministic calculations.

Technical-analysis prompts should receive compact deterministic context rather
than complete historical series. Use the agreed 20-trading-day recent window
and 60-trading-day quarterly window when available, plus price-versus-SMA
relationships. Keep the calculations in Python and let the LLM explain them.
* **Deterministic:** the same input and conditions produce the same result.
* **Vertical slice:** a small feature that works from input to visible output.

For LLM features, prefer a visible LangChain chain such as
`prompt | model | structured output`. Use LangChain's provider-aware structured
output for typed reports instead of inspecting raw provider response objects.
Use a text parser only for intentionally plain-text results. Use LangGraph `StateGraph` for
application-level state, nodes, edges, and multi-agent routing—not as a hidden
replacement for the small chains inside those nodes.

If a term is not in this list and is not obvious to a new contributor, define it
near its first use.

## Formatting

Use Ruff formatter.

Formatting should be automatic whenever possible.

---

## Linting

Use Ruff.

All linting issues should be resolved before committing.

---

## Static Type Checking

Use MyPy.

Requirements:

* Complete type hints
* Avoid `Any` whenever practical
* Public APIs must be fully typed

---

## Runtime Validation

Use Pydantic v2.

Use models for:

* API responses
* configuration
* structured LLM outputs
* internal data models

Avoid dictionaries where structured models provide better clarity.

---

# Function Design

Functions should:

* have a single responsibility
* remain small and readable
* use descriptive names
* avoid hidden side effects

Prefer functions under approximately 50 lines.

---

# Class Design

Prefer composition over inheritance.

Avoid "God classes."

Use dependency injection where it improves testability.

Keep responsibilities focused.

---

# Documentation

All public modules, classes, and functions should include concise Google-style docstrings.

Comments should explain **why**, not **what**.

Complex architectural decisions deserve brief explanations.

---

# Prompt Management

Prompt templates are kept separate from agent logic. The current MVP stores
them as provider-neutral LangChain `ChatPromptTemplate` objects in `app/prompts/`.

Local API keys may be stored in `~/.secrets/.env`, which the application loads
automatically. The file must remain outside the repository. Use
`OPENAI_API_KEY` and `GOOGLE_API_KEY`; the legacy typo `OPENAI_AI_KEY` is
accepted for compatibility but should not be used in new files.

Location:

```text
prompts/
```

Prompts should:

* be version controlled
* be reusable
* be easy to modify
* avoid embedded business logic

---

# Logging

Use Python's logging module.

Never use `print()` for production code.

Logs should include:

* timestamp
* log level
* module
* meaningful message

---

# Error Handling

Handle expected exceptions explicitly.

Never silently ignore exceptions.

Provide informative log messages.

User-facing errors should remain clear and understandable.

---

# Testing

Testing framework:

* pytest

Every deterministic module should have unit tests.

Focus testing on:

* business logic
* calculations
* services
* utilities
* data transformations

LLM wording itself generally does not require unit tests.

## Testing Strategy

For the Streamlit interface, keep the first testing layer small: use
`streamlit.testing.v1.AppTest` for page-load, widget, mocked-result, and error
smoke tests. Do not make real market-data or LLM calls from UI tests. Defer
Playwright until browser or deployed-application behavior needs verification;
Robot Framework is not part of the planned test stack.

Add tests at the same time as the behavior they protect. The current project
uses schema, deterministic calculation, mocked service, flow, and CLI tests.
When an agent is added, add mocked-LLM tests and output-schema checks first.
Then add fixed example evaluations and human review. LLM-as-judge checks are
optional regression evaluations for report quality; they do not replace normal
tests and should not be introduced before the agent produces real reports.

## Coverage

Coverage is initially a visibility metric rather than a hard quality gate. Run:

```text
pytest --cov=app --cov-report=term-missing
```

Coverage should be reported in CI and reviewed for deterministic calculations,
schemas, data transformations, and service error handling. A minimum threshold can
be introduced after the MVP establishes a baseline.

---

# Code Quality Workflow

Before code is considered complete, it should pass:

```text
ruff check

ruff format

mypy .

pytest

bandit -r app

pytest --cov=app --cov-report=term-missing
```

The repository also uses pre-commit hooks to run local checks before commits:
Ruff check, Ruff formatting verification, MyPy, pytest, Bandit, and Gitleaks.
MyPy and pytest run when Python files under `app/` or `tests/` are changed;
Bandit runs when application Python files change. Coverage is a separate
reporting command and is not a pre-commit hook.

---

# Git Workflow

The project follows a feature branch workflow.

General process:

```text
main

↓

git pull

↓

feature/my-feature

↓

development

↓

git merge

↓

main

↓

git push
```

Guidelines:

* Keep `main` usable and deployable.
* Use a feature or release branch for a coherent release scope; a new branch is
  not required for every small backlog task.
* Pull requests are optional for this solo project; local review and merge are acceptable.
* Implement and test one stable task slice at a time.
* Create one focused local commit per tested task slice. The AI coding agent may
  create these commits only when explicitly authorized for the current branch.
* The human developer exclusively owns pushes to GitHub, merges, remote tags,
  releases, and all changes to `main`. The AI coding agent must not perform
  those remote or release operations.
* Delete a feature branch after it has been merged and verified

---

# Commit Messages

Use Conventional Commits.

Examples:

```text id="3iqek2"
feat(options): add option chain service

fix(config): resolve env loading

refactor(graph): simplify supervisor

test(tools): add RSI tests

docs: update architecture
```

Keep the commit header under approximately 50 characters.

---

# Continuous Integration

GitHub Actions runs the checks on pushes to `main` and on pull requests. The
same checks should still be run locally before pushing:

CI should verify:

* Ruff
* MyPy
* pytest
* Bandit
* coverage reporting
* Grype image scanning for Docker build workflows

Dependabot alerts are enabled through GitHub for the dependency manifests.

The reasoning behind major workflow decisions is recorded in the
[architecture decision records](decisions/README.md), and project lessons are
kept in the private learning journal.

The local development workflow should mirror CI as closely as possible.

## Practical local and CI/CD workflows

Use the smallest workflow that matches the change:

### Local development

```text
edit → run tests → optionally build/run Docker Compose
```

Run tests and quality checks for ordinary Python changes. Build Docker images
and run Docker Compose when changing Dockerfiles, Compose configuration,
dependencies, service startup, or deployment behavior. Docker image builds are
intentional and do not need to run for every code edit.

### Pull requests

```text
push branch → GitHub runs tests, builds images, scans images, and reports results
```

GitHub Actions builds the service images in a clean runner and scans them with
Grype. Pull-request workflows do not push images to a registry or deploy
services.

### Main and releases

```text
merge → GitHub builds and scans release images →
pushes to Artifact Registry → deploys Cloud Run
```

The detailed trigger policy is:

```text
Pull request:
  run tests
  build images
  run Grype scans
  do not deploy

Push to main:
  run tests
  build and scan images
  do not push images or deploy automatically

Release tag, for example v0.17.0:
  build and scan images
  push images to Artifact Registry
  deploy to Cloud Run
```

This keeps ordinary merges inexpensive and makes cloud deployment an explicit
release action.

Run the local Streamlit interface from the project root with:

```text
streamlit run streamlit_app.py
```

---

# Release Process

Each release should include concise release notes describing:

* what was implemented
* why it was implemented
* lessons learned or improvements

Releases should represent meaningful, working milestones. Publish releases from
verified commits on `main` using semantic-version Git tags such as `v0.1.0` and
`v0.2.0`. A pull request is not required to publish a release.

---

# Definition of Done

A task is complete when:

* Functionality works as intended
* Architecture principles are respected
* Code remains simple and maintainable
* Ruff passes
* MyPy passes
* pytest passes
* Appropriate documentation has been updated
* No unnecessary complexity has been introduced

Quality is measured by correctness, maintainability, readability, and long-term sustainability—not by the amount of code written.
