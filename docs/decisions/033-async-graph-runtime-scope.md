# ADR-033: Keep the asynchronous graph scope focused

## Decision

Use a separate asynchronous StateGraph path only for concurrent Market Context
and Ticker News execution. Keep Technical Analysis before those branches and
Options Analysis and Recommendation after they join. The synchronous graph
remains the Streamlit reference path until the FastAPI phase.

Run the async path in a long-running server runtime. Do not add application
logic to manage LangGraph's internal worker-thread cleanup for one-shot
`asyncio.run()` calls.

## Rationale

The goal of PB-031 is to learn task coordination and reduce waiting for the two
independent contextual analyses, not to convert every provider and node to
fully asynchronous code. Investigation showed that the graph returns the
correct result but may leave an idle internal executor thread after standalone
execution. Managing that implementation detail would add complexity without
improving the workflow result.

## Consequences

- FastAPI is the intended runtime for the async graph.
- Streamlit continues to use the stable synchronous graph in this phase.
- Blocking provider and LLM runners remain wrapped by the existing async
  adapters.
- The async path keeps explicit timeouts, partial-report warnings, and state
  validation.
- A future high-concurrency deployment may revisit fully async clients or
  explicit concurrency limits.
