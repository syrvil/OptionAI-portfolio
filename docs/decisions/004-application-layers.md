# ADR-004: Layer the application into schemas, services, tools, and agents

* Status: Accepted
* Date: 2026-08-07

## Decision

Keep deterministic responsibilities separated into schemas, services, and
tools, with agents coordinating those tools and explaining results.

## Rationale

Schemas define data contracts, services handle external data and integrations,
and tools expose safe, focused capabilities to agents. This keeps business
logic testable and transparent while allowing agent behavior to evolve
independently.
