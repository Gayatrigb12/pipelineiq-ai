from __future__ import annotations

import logging
from typing import Sequence

from langchain_core.documents import Document

from app.schemas.deal_schema import DealBase
from app.vectorstore.chroma_store import create_vectorstore, load_vectorstore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document conversion
# ---------------------------------------------------------------------------


def _deal_to_document(deal: DealBase) -> Document:
    """
    Convert a single :class:`DealBase` instance into a LangChain
    :class:`Document`.

    * **page_content** – a human-readable prose summary suitable for
      semantic embedding and retrieval.
    * **metadata** – structured fields stored alongside the vector so
      that results can be filtered or surfaced in answers.
    """
    page_content = (
        f"Deal Name: {deal.deal_name}\n"
        f"Company: {deal.company}\n"
        f"Value: ${deal.value:,.2f}\n"
        f"Stage: {deal.stage.value}\n"
        f"Owner: {deal.owner}\n"
        f"Last Activity Date: {deal.last_activity_date.isoformat()}\n"
        f"Lead Source: {deal.lead_source.value}\n"
        f"Industry: {deal.industry.value}\n"
        f"Days in Stage: {deal.days_in_stage}\n"
        f"Notes: {deal.notes or 'N/A'}"
    )

    metadata: dict[str, str | int | float] = {
        # Required metadata (per specification)
        "company": deal.company,
        "owner": deal.owner,
        "stage": deal.stage.value,
        # Additional metadata for richer filtering / attribution
        "deal_name": deal.deal_name,
        "lead_source": deal.lead_source.value,
        "industry": deal.industry.value,
        "days_in_stage": deal.days_in_stage,
        "last_activity_date": deal.last_activity_date.isoformat(),
        "value": float(deal.value),
    }

    return Document(page_content=page_content, metadata=metadata)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ingest_deals(
    deals: Sequence[DealBase],
    *,
    overwrite: bool = False,
) -> int:
    """
    Embed *deals* and upsert them into the persistent ChromaDB vector store.

    Args:
        deals:      Iterable of :class:`DealBase` (or any subclass) instances.
        overwrite:  When ``True``, always call :func:`create_vectorstore` and
                    replace any existing collection.  When ``False`` (default),
                    the function attempts to *add* documents to an existing
                    store and falls back to creating a new one if none exists.

    Returns:
        Number of documents ingested.

    Raises:
        ValueError: If *deals* is empty.
    """
    if not deals:
        raise ValueError("No deals provided — ingestion aborted.")

    documents: list[Document] = [_deal_to_document(d) for d in deals]

    logger.info("Converting %d deal(s) to LangChain Documents …", len(documents))

    if overwrite:
        logger.info("overwrite=True — creating a fresh vector store.")
        create_vectorstore(documents)
    else:
        try:
            vectorstore = load_vectorstore()
            logger.info("Existing vector store found — adding documents.")
            vectorstore.add_documents(documents)
        except FileNotFoundError:
            logger.info("No existing vector store found — creating a new one.")
            create_vectorstore(documents)

    logger.info("Successfully ingested %d deal document(s).", len(documents))
    return len(documents)