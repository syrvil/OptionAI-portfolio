"""Sanitized portfolio example for a market-context prompt."""

from langchain_core.prompts import ChatPromptTemplate

MARKET_CONTEXT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Summarize the supplied market-context inputs. Use only the provided
headlines and metadata. Describe themes, evidence, risks, and limitations.
State uncertainty when the sample is incomplete or conflicting. Do not give
an investment instruction. Return the structured market-context fields.""",
        ),
        ("human", "Market news input:\n{market_news}"),
    ]
)
