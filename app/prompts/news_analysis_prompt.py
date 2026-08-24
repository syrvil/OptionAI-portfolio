"""Sanitized portfolio example for a ticker-news prompt."""

from langchain_core.prompts import ChatPromptTemplate

NEWS_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Summarize the supplied ticker-specific news. Use only the provided "
            "headlines and metadata. Return themes, evidence, risks, and "
            "limitations in the required schema. Do not give an investment "
            "instruction and state uncertainty when the input is limited.",
        ),
        (
            "human",
            "Ticker news input:\n{ticker_news}",
        ),
    ]
)
