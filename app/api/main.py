"""FastAPI application for the OptionAI backend."""

import logging
from datetime import date
from typing import cast

from fastapi import FastAPI, HTTPException

from app.graph.state import AnalysisState
from app.graph.workflow import (
    build_analysis_graph,
    build_async_analysis_graph,
    build_async_continuation_graph,
    invoke_analysis_graph_async,
)
from app.schemas.analysis_api import (
    AnalysisApiRequest,
    AnalysisApiResponse,
    AnalysisContinuationRequest,
)
from app.schemas.market_data import PriceHistoryRequest
from app.services.market_data import MarketDataError
from app.tools.technical_analysis_runner import run_technical_analysis

logger = logging.getLogger(__name__)

app = FastAPI(title="OptionAI API", version="0.10.0")
analysis_graph = build_analysis_graph()
async_analysis_graph = build_async_analysis_graph()
async_continuation_graph = build_async_continuation_graph()


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is running."""
    return {"status": "ok"}


@app.post("/analysis", response_model=AnalysisApiResponse)
def analysis(request: AnalysisApiRequest) -> AnalysisApiResponse:
    """Run the composed synchronous analysis workflow."""
    try:
        if request.end_date < date.today():
            report = run_technical_analysis(
                PriceHistoryRequest(
                    ticker=request.ticker,
                    start_date=request.start_date,
                    end_date=request.end_date,
                )
            )
            state: AnalysisState = {
                "ticker": request.ticker,
                "options_strategy": None,
                "technical_analysis_report": report,
                "status": "awaiting_strategy",
                "warnings": [],
                "error": None,
            }
        else:
            state = cast(
                AnalysisState,
                analysis_graph.invoke(cast(AnalysisState, request.model_dump())),
            )
    except (ValueError, MarketDataError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Synchronous analysis workflow failed")
        raise HTTPException(
            status_code=500, detail="analysis workflow failed"
        ) from error
    return AnalysisApiResponse.model_validate(state)


@app.post("/analysis/async", response_model=AnalysisApiResponse)
async def analysis_async(request: AnalysisApiRequest) -> AnalysisApiResponse:
    """Run the composed analysis workflow through the async graph."""
    if request.end_date < date.today():
        return analysis(request)
    try:
        state = await invoke_analysis_graph_async(
            async_analysis_graph,
            cast(AnalysisState, request.model_dump()),
        )
    except (ValueError, MarketDataError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Asynchronous analysis workflow failed")
        raise HTTPException(
            status_code=500, detail="analysis workflow failed"
        ) from error
    return AnalysisApiResponse.model_validate(state)


@app.post("/analysis/continue", response_model=AnalysisApiResponse)
async def analysis_continue(
    request: AnalysisContinuationRequest,
) -> AnalysisApiResponse:
    """Continue from validated initial reports after strategy selection."""
    try:
        state = await invoke_analysis_graph_async(
            async_continuation_graph,
            cast(
                AnalysisState,
                {
                    "ticker": request.ticker,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "options_strategy": request.options_strategy,
                    "technical_analysis_report": request.technical_analysis_report,
                    "market_context_report": request.market_context_report,
                    "news_report": request.news_report,
                },
            ),
        )
    except (ValueError, MarketDataError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Asynchronous continuation workflow failed")
        raise HTTPException(
            status_code=500, detail="analysis continuation failed"
        ) from error
    return AnalysisApiResponse.model_validate(state)
