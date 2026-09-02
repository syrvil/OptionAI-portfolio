# LLM evaluation — portfolio overview

The private project uses a small, repeatable local process to evaluate model
and prompt changes. The public portfolio shows the process without publishing
private test data, production prompts, or business rules.

## Process

```text
Versioned frozen cases → one model or prompt configuration
                       → deterministic checks and measurements
                       → one Markdown review packet
                       → manual review and JSON/Markdown summary
                       → version-controlled evaluation registry
```

The same cases are used for each configuration. The current case set covers
Technical Analysis only. Market Context is the next planned agent, followed by
Ticker News, Options, and Recommendation.

## Review responsibilities

Automated checks verify schema validity, preservation of supplied facts, and
measurements such as latency. They complement pytest: pytest checks the
application implementation, while evaluation checks whether a selected model
produces a correct explanation of frozen facts.

Manual review is currently the preferred quality assessment. An LLM judge is
available as an experimental advisory second opinion, but is not treated as
ground truth or as a merge gate.

## Stored artifacts

The private project stores each test run separately with generated results, an
optional judge review, a Markdown review packet, and JSON/Markdown summaries.
A flat registry records selected historical summaries. The public portfolio
does not include generated artifacts because they may expose private prompts,
data, or implementation details.
