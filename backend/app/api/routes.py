from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.schemas.deal_schema import DealCreate
from app.services.ingestion_service import ingest_deals
from app.services.rag_service import ask_question

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Shared response schemas
# ---------------------------------------------------------------------------


class UploadDealsResponse(BaseModel):
    success: bool = True
    message: str
    deals_ingested: int


# ---------------------------------------------------------------------------
# POST /upload-deals
# ---------------------------------------------------------------------------


class UploadDealsRequest(BaseModel):
    deals: Annotated[
        list[DealCreate],
        Field(min_length=1, description="One or more deals to embed and store."),
    ]


@router.post(
    "/upload-deals",
    response_model=UploadDealsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest deals into the vector knowledge base",
    tags=["Deals"],
)
async def upload_deals(payload: UploadDealsRequest) -> UploadDealsResponse:
    """
    Accept a list of CRM deal objects, convert them to embeddings, and
    persist them in ChromaDB for downstream RAG retrieval.
    """
    try:
        count = ingest_deals(payload.deals)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Failed to ingest deals.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while storing deals. Please try again.",
        ) from exc

    return UploadDealsResponse(
        success=True,
        message="Deals ingested successfully.",
        deals_ingested=count,
    )


# ---------------------------------------------------------------------------
# POST /chat
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a natural-language question about the deal pipeline",
    tags=["Chat"],
)
async def chat(payload: ChatRequest) -> ChatResponse:
    """
    Run a RAG query against the persisted ChromaDB deal knowledge base
    and return a model-generated answer.
    """
    try:
        answer = ask_question(payload.question)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The deal knowledge base is empty. "
                "Please upload deals via POST /upload-deals first."
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("RAG query failed for question: %r", payload.question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question. Please try again.",
        ) from exc

    return ChatResponse(answer=answer)

# ---------------------------------------------------------------------------
# GET /dashboard-stats
# ---------------------------------------------------------------------------

@router.get("/dashboard-stats")
async def dashboard_stats():
    return {
        "total_deals": 10,
        "pipeline_value": 4220000,
        "closed_deals": 2,
        "win_rate": 20
    }