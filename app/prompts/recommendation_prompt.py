"""Sanitized portfolio examples for recommendation prompts."""

from langchain_core.prompts import ChatPromptTemplate

RECOMMENDATION_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Classify each supplied report as supporting, neutral, or conflicting
with the selected user strategy. Use only validated report facts and explain
each classification briefly. Do not invent missing reports or change the
strategy. Return the required classification schema.""",
        ),
        ("human", "Strategy and report facts:\n{recommendation_facts}"),
    ]
)

RECOMMENDATION_EXPLANATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Explain the supplied deterministic outcome using the validated
classifications and report facts. Do not change the strategy, classifications,
or outcome, and do not calculate new metrics. Return a concise structured
explanation with evidence, risks, and limitations.""",
        ),
        (
            "human",
            "Strategy and report facts:\n{recommendation_facts}\n\n"
            "Classifications:\n{classifications}\n\n"
            "Deterministic outcome: {deterministic_outcome}",
        ),
    ]
)

RECOMMENDATION_PROMPT = RECOMMENDATION_CLASSIFICATION_PROMPT
