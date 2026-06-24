# from __future__ import annotations

# import logging

# from langchain.chains import RetrievalQA
# from langchain_core.prompts import PromptTemplate

# from app.core.llm import get_llm
# from app.vectorstore.chroma_store import load_vectorstore

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # Prompt
# # ---------------------------------------------------------------------------

# _PROMPT_TEMPLATE = """You are PipelineIQ, an expert AI Revenue Copilot.
# Use the following CRM deal context to answer the question accurately and concisely.
# If the answer cannot be determined from the context, say so clearly — do not speculate.

# Context:
# {context}

# Question: {question}

# Answer:"""

# _PROMPT = PromptTemplate(
#     template=_PROMPT_TEMPLATE,
#     input_variables=["context", "question"],
# )

# # ---------------------------------------------------------------------------
# # Chain factory
# # ---------------------------------------------------------------------------

# _RETRIEVER_SEARCH_KWARGS: dict = {"k": 5}


# def _build_chain() -> RetrievalQA:
#     """Construct the RetrievalQA chain from the persisted vector store."""
#     vectorstore = load_vectorstore()

#     retriever = vectorstore.as_retriever(
#         search_type="similarity",
#         search_kwargs=_RETRIEVER_SEARCH_KWARGS,
#     )

#     chain = RetrievalQA.from_chain_type(
#         llm=get_llm(),
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=False,
#         chain_type_kwargs={"prompt": _PROMPT},
#     )

#     return chain


# # ---------------------------------------------------------------------------
# # Public API
# # ---------------------------------------------------------------------------


# def ask_question(question: str) -> str:
#     """
#     Run a RAG query against the persisted ChromaDB deal knowledge base.

#     Args:
#         question: Natural-language question about the deal pipeline.

#     Returns:
#         The model-generated answer as a plain string.

#     Raises:
#         FileNotFoundError: If no vector store has been created yet.
#         ValueError: If *question* is empty.
#     """
#     if not question or not question.strip():
#         raise ValueError("Question must not be empty.")

#     logger.info("RAG query received: %r", question)

#     chain = _build_chain()
#     result: dict = chain.invoke({"query": question})
#     answer: str = result.get("result", "").strip()

#     logger.info("RAG answer generated (%d chars).", len(answer))
#     return answer

from __future__ import annotations

import logging

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from app.core.llm import get_llm
from app.vectorstore.chroma_store import load_vectorstore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stage classification constants
# ---------------------------------------------------------------------------

# Stages that represent terminal / closed outcomes
CLOSED_STAGES: frozenset[str] = frozenset({"closed_won", "closed_lost"})

# Stages that count toward active pipeline value
ACTIVE_PIPELINE_STAGES: frozenset[str] = frozenset({
    "prospecting",
    "qualification",
    "proposal",
    "negotiation",
})

# ---------------------------------------------------------------------------
# Prompt — strict filtering and aggregation rules baked in
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """You are PipelineIQ, an expert AI Revenue Copilot embedded in a CRM analytics system.
Answer the user's question using ONLY the deal context provided below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT CALCULATION RULES — YOU MUST FOLLOW THESE EXACTLY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ACTIVE PIPELINE VALUE
   - Include ONLY deals with Stage in: prospecting, qualification, proposal, negotiation
   - NEVER include closed_won or closed_lost deals in pipeline value or pipeline counts
   - Pipeline Value = sum of "Value" fields for active-stage deals only

2. CLOSED WON
   - Include ONLY deals where Stage = closed_won
   - Closed Won Revenue = sum of "Value" fields for closed_won deals only

3. CLOSED LOST
   - Include ONLY deals where Stage = closed_lost
   - NEVER add closed_lost value to pipeline or won revenue

4. WIN RATE
   - Win Rate = (number of closed_won deals) / (number of closed_won + number of closed_lost deals) × 100
   - ONLY compute win rate when both closed_won and closed_lost deals are present in context

5. RISK ASSESSMENT
   - A deal is at risk if: days_in_stage > 30 AND stage is NOT closed_won AND stage is NOT closed_lost
   - Always cite days_in_stage and last_activity_date as evidence when flagging risk

6. AGGREGATION INTEGRITY
   - Never combine values across different stage groups
   - Never assume a deal's value if it is not explicitly stated in context
   - Never invent deals not present in the context
   - If the context does not contain enough data to answer, say: "Insufficient data in the current knowledge base to answer this accurately."

7. OUTPUT FORMAT
   - For lists: bullet each deal with deal_name, company, stage, value, owner
   - For totals: show the calculation (e.g. "$320,000 + $215,000 = $535,000")
   - For risk: always state days_in_stage and last_activity_date
   - Be concise and factual — no speculation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEAL CONTEXT (retrieved from knowledge base):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTION: {question}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANSWER:"""

_PROMPT = PromptTemplate(
    template=_PROMPT_TEMPLATE,
    input_variables=["context", "question"],
)

# ---------------------------------------------------------------------------
# Question routing — detect aggregation intent to widen retrieval
# ---------------------------------------------------------------------------

_AGGREGATION_KEYWORDS: frozenset[str] = frozenset({
    "total", "sum", "pipeline", "value", "revenue", "count",
    "how many", "win rate", "aggregate", "all deals", "overview",
    "dashboard", "report", "breakdown",
})


def _is_aggregation_query(question: str) -> bool:
    """Return True if the question requires aggregating across all deals."""
    q = question.lower()
    return any(kw in q for kw in _AGGREGATION_KEYWORDS)


def _get_retriever_k(question: str) -> int:
    """
    Return a wider k for aggregation queries so the LLM sees all relevant deals.
    Default k=6 for targeted questions, k=20 for aggregation/pipeline questions.
    """
    return 20 if _is_aggregation_query(question) else 6


# ---------------------------------------------------------------------------
# Chain factory
# ---------------------------------------------------------------------------


def _build_chain(k: int) -> RetrievalQA:
    """Construct the RetrievalQA chain with the given retriever k."""
    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

    chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": _PROMPT},
    )

    return chain


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ask_question(question: str) -> str:
    """
    Run a RAG query against the persisted ChromaDB deal knowledge base.

    Stage filtering and aggregation rules are enforced via the system prompt.
    Retriever k is widened automatically for aggregation/pipeline questions.

    Args:
        question: Natural-language question about the deal pipeline.

    Returns:
        The model-generated answer as a plain string.

    Raises:
        FileNotFoundError: If no vector store has been created yet.
        ValueError: If *question* is empty.
    """
    if not question or not question.strip():
        raise ValueError("Question must not be empty.")

    k = _get_retriever_k(question)
    logger.info("RAG query received (k=%d): %r", k, question)

    chain = _build_chain(k)
    result: dict = chain.invoke({"query": question})
    answer: str = result.get("result", "").strip()

    if not answer:
        answer = (
            "Insufficient data in the current knowledge base to answer this accurately. "
            "Please ensure deals have been uploaded via POST /upload-deals."
        )

    logger.info("RAG answer generated (%d chars).", len(answer))
    return answer