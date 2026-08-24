"""Sanitized portfolio example for a technical-analysis prompt."""

from langchain_core.prompts import ChatPromptTemplate

TECHNICAL_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Analyze the validated technical facts supplied by the application.
Use only those facts. Explain the observed condition, supporting evidence,
risks, limitations, and conditions that could invalidate the interpretation.
Do not calculate new values, call tools, or provide a trading instruction.
Return the structured fields required by the technical-analysis schema.""",
        ),
        ("human", "Validated technical facts:\n{technical_data}"),
    ]
)
