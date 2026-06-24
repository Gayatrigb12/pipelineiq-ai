# from __future__ import annotations

# import logging
# from typing import Sequence

# from langchain_core.documents import Document

# from app.schemas.deal_schema import DealBase
# from app.vectorstore.chroma_store import create_vectorstore, load_vectorstore

# logger = logging.getLogger(__name__)


# # ---------------------------------------------------------------------------
# # Document conversion
# # ---------------------------------------------------------------------------


# def _deal_to_document(deal: DealBase) -> Document:
#     """
#     Convert a single :class:`DealBase` instance into a LangChain
#     :class:`Document`.

#     * **page_content** – a human-readable prose summary suitable for
#       semantic embedding and retrieval.
#     * **metadata** – structured fields stored alongside the vector so
#       that results can be filtered or surfaced in answers.
#     """
#     page_content = (
#         f"Deal Name: {deal.deal_name}\n"
#         f"Company: {deal.company}\n"
#         f"Value: ${deal.value:,.2f}\n"
#         f"Stage: {deal.stage.value}\n"
#         f"Owner: {deal.owner}\n"
#         f"Last Activity Date: {deal.last_activity_date.isoformat()}\n"
#         f"Lead Source: {deal.lead_source.value}\n"
#         f"Industry: {deal.industry.value}\n"
#         f"Days in Stage: {deal.days_in_stage}\n"
#         f"Notes: {deal.notes or 'N/A'}"
#     )

#     metadata: dict[str, str | int | float] = {
#         # Required metadata (per specification)
#         "company": deal.company,
#         "owner": deal.owner,
#         "stage": deal.stage.value,
#         # Additional metadata for richer filtering / attribution
#         "deal_name": deal.deal_name,
#         "lead_source": deal.lead_source.value,
#         "industry": deal.industry.value,
#         "days_in_stage": deal.days_in_stage,
#         "last_activity_date": deal.last_activity_date.isoformat(),
#         "value": float(deal.value),
#     }

#     return Document(page_content=page_content, metadata=metadata)


# # ---------------------------------------------------------------------------
# # Public API
# # ---------------------------------------------------------------------------


# def ingest_deals(
#     deals: Sequence[DealBase],
#     *,
#     overwrite: bool = False,
# ) -> int:
#     """
#     Embed *deals* and upsert them into the persistent ChromaDB vector store.

#     Args:
#         deals:      Iterable of :class:`DealBase` (or any subclass) instances.
#         overwrite:  When ``True``, always call :func:`create_vectorstore` and
#                     replace any existing collection.  When ``False`` (default),
#                     the function attempts to *add* documents to an existing
#                     store and falls back to creating a new one if none exists.

#     Returns:
#         Number of documents ingested.

#     Raises:
#         ValueError: If *deals* is empty.
#     """
#     if not deals:
#         raise ValueError("No deals provided — ingestion aborted.")

#     documents: list[Document] = [_deal_to_document(d) for d in deals]

#     logger.info("Converting %d deal(s) to LangChain Documents …", len(documents))

#     if overwrite:
#         logger.info("overwrite=True — creating a fresh vector store.")
#         create_vectorstore(documents)
#     else:
#         try:
#             vectorstore = load_vectorstore()
#             logger.info("Existing vector store found — adding documents.")
#             vectorstore.add_documents(documents)
#         except FileNotFoundError:
#             logger.info("No existing vector store found — creating a new one.")
#             create_vectorstore(documents)

#     logger.info("Successfully ingested %d deal document(s).", len(documents))
#     return len(documents)

from __future__ import annotations

import logging
from typing import Sequence

from langchain_core.documents import Document

from app.schemas.deal_schema import DealBase, DealStage
from app.vectorstore.chroma_store import create_vectorstore, load_vectorstore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stage classification constants (mirrors rag_service.py)
# ---------------------------------------------------------------------------

ACTIVE_PIPELINE_STAGES: frozenset[str] = frozenset({
    DealStage.PROSPECTING,
    DealStage.QUALIFICATION,
    DealStage.PROPOSAL,
    DealStage.NEGOTIATION,
})

CLOSED_STAGES: frozenset[str] = frozenset({
    DealStage.CLOSED_WON,
    DealStage.CLOSED_LOST,
})


def _pipeline_classification(stage_value: str) -> str:
    """
    Return an explicit pipeline classification label for the deal's stage.
    This is embedded into page_content so the LLM never mis-classifies a deal.
    """
    if stage_value in ACTIVE_PIPELINE_STAGES:
        return "ACTIVE_PIPELINE"
    if stage_value == DealStage.CLOSED_WON:
        return "CLOSED_WON — exclude from active pipeline"
    if stage_value == DealStage.CLOSED_LOST:
        return "CLOSED_LOST — exclude from pipeline and revenue"
    return "UNKNOWN"


def _risk_flag(deal: DealBase) -> str:
    """
    Return a pre-computed risk label so the LLM doesn't have to infer it.
    A deal is AT_RISK when days_in_stage > 30 and it is not in a closed stage.
    """
    stage_value = deal.stage.value
    if stage_value in CLOSED_STAGES:
        return "N/A (closed)"
    if deal.days_in_stage > 30:
        return f"AT_RISK — {deal.days_in_stage} days in stage (threshold: 30)"
    return f"OK — {deal.days_in_stage} days in stage"


# ---------------------------------------------------------------------------
# Document conversion
# ---------------------------------------------------------------------------


def _deal_to_document(deal: DealBase) -> Document:
    """
    Convert a single :class:`DealBase` instance into a LangChain
    :class:`Document`.

    page_content includes:
    - All deal fields in labelled prose (optimised for semantic embedding)
    - Explicit pipeline classification label (prevents LLM stage mis-grouping)
    - Pre-computed risk flag (prevents LLM from guessing threshold)

    metadata includes structured fields for Chroma metadata filtering.
    """
    stage_value = deal.stage.value
    pipeline_class = _pipeline_classification(stage_value)
    risk_flag = _risk_flag(deal)

    page_content = (
        f"Deal Name: {deal.deal_name}\n"
        f"Company: {deal.company}\n"
        f"Value: ${deal.value:,.2f}\n"
        f"Stage: {stage_value}\n"
        f"Pipeline Classification: {pipeline_class}\n"
        f"Risk Flag: {risk_flag}\n"
        f"Owner: {deal.owner}\n"
        f"Last Activity Date: {deal.last_activity_date.isoformat()}\n"
        f"Lead Source: {deal.lead_source.value}\n"
        f"Industry: {deal.industry.value}\n"
        f"Days in Stage: {deal.days_in_stage}\n"
        f"Notes: {deal.notes or 'N/A'}"
    )

    metadata: dict[str, str | int | float] = {
        # Core filter fields
        "company":        deal.company,
        "owner":          deal.owner,
        "stage":          stage_value,
        # Pre-computed classification — lets downstream filtering bypass LLM guessing
        "pipeline_class": pipeline_class,
        "is_active_pipeline": int(stage_value in ACTIVE_PIPELINE_STAGES),
        "is_closed_won":  int(stage_value == DealStage.CLOSED_WON),
        "is_closed_lost": int(stage_value == DealStage.CLOSED_LOST),
        "is_at_risk":     int(
            deal.days_in_stage > 30 and stage_value not in CLOSED_STAGES
        ),
        # Quantitative fields
        "value":          float(deal.value),
        "days_in_stage":  deal.days_in_stage,
        # Attribution / grouping fields
        "deal_name":      deal.deal_name,
        "lead_source":    deal.lead_source.value,
        "industry":       deal.industry.value,
        "last_activity_date": deal.last_activity_date.isoformat(),
    }

    return Document(page_content=page_content, metadata=metadata)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_deals(deals: Sequence[DealBase]) -> None:
    """
    Pre-ingestion validation guard.
    Raises ValueError with a descriptive message on any structural issue.
    """
    if not deals:
        raise ValueError("No deals provided — ingestion aborted.")

    valid_stages = {s.value for s in DealStage}
    errors: list[str] = []

    for i, deal in enumerate(deals):
        stage_value = deal.stage.value if hasattr(deal.stage, "value") else str(deal.stage)
        if stage_value not in valid_stages:
            errors.append(
                f"Deal[{i}] '{deal.deal_name}': invalid stage '{stage_value}'. "
                f"Must be one of: {sorted(valid_stages)}"
            )
        if float(deal.value) < 0:
            errors.append(
                f"Deal[{i}] '{deal.deal_name}': value ${deal.value} is negative."
            )
        if deal.days_in_stage < 0:
            errors.append(
                f"Deal[{i}] '{deal.deal_name}': days_in_stage {deal.days_in_stage} is negative."
            )

    if errors:
        raise ValueError(
            f"Ingestion validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  • {e}" for e in errors)
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ingest_deals(
    deals: Sequence[DealBase],
    *,
    overwrite: bool = False,
) -> int:
    """
    Validate, embed, and upsert deals into the persistent ChromaDB vector store.

    Validation runs before any embedding or DB operation so bad data never
    reaches the vector store.

    Args:
        deals:      Iterable of :class:`DealBase` (or any subclass) instances.
        overwrite:  When ``True``, always call :func:`create_vectorstore` and
                    replace any existing collection.  When ``False`` (default),
                    the function attempts to *add* documents to an existing
                    store and falls back to creating a new one if none exists.

    Returns:
        Number of documents ingested.

    Raises:
        ValueError: If *deals* is empty or fails structural validation.
    """
    # ── 1. Validate before touching the DB ────────────────────────────────
    _validate_deals(deals)

    # ── 2. Log stage breakdown for audit trail ─────────────────────────────
    stage_counts: dict[str, int] = {}
    for d in deals:
        stage_counts[d.stage.value] = stage_counts.get(d.stage.value, 0) + 1
    logger.info("Stage breakdown for ingestion batch: %s", stage_counts)

    active_count = sum(
        1 for d in deals if d.stage.value in ACTIVE_PIPELINE_STAGES
    )
    closed_won_count = sum(
        1 for d in deals if d.stage.value == DealStage.CLOSED_WON
    )
    closed_lost_count = sum(
        1 for d in deals if d.stage.value == DealStage.CLOSED_LOST
    )
    active_pipeline_value = sum(
        float(d.value) for d in deals if d.stage.value in ACTIVE_PIPELINE_STAGES
    )
    logger.info(
        "Batch summary — active: %d ($%.2f), closed_won: %d, closed_lost: %d",
        active_count, active_pipeline_value, closed_won_count, closed_lost_count,
    )

    # ── 3. Convert to LangChain Documents ─────────────────────────────────
    documents: list[Document] = [_deal_to_document(d) for d in deals]
    logger.info("Converted %d deal(s) to LangChain Documents.", len(documents))

    # ── 4. Persist to ChromaDB ─────────────────────────────────────────────
    if overwrite:
        logger.info("overwrite=True — creating a fresh vector store.")
        create_vectorstore(documents)
    else:
        try:
            vectorstore = load_vectorstore()
            logger.info("Existing vector store found — adding documents.")
            vectorstore.add_documents(documents)
        except FileNotFoundError:
            logger.info("No existing vector store — creating a new one.")
            create_vectorstore(documents)

    logger.info("Successfully ingested %d deal document(s).", len(documents))
    return len(documents)