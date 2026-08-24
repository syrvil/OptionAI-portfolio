"""Sanitized portfolio example for an options-analysis prompt."""

from langchain_core.prompts import ChatPromptTemplate

OPTIONS_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Explain the supplied, validated options facts. Do not calculate new
metrics, invent missing values, or turn the analysis into a trading instruction.
Describe evidence, risks, limitations, and uncertainty using the required
options-analysis schema.""",
        ),
        ("human", "Here are the validated options facts:\n{options_data}"),
    ]
)
