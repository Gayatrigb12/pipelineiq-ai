from __future__ import annotations

import logging

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from app.core.llm import get_llm
from app.vectorstore.chroma_store import load_vectorstore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """You are PipelineIQ, an expert AI Revenue Copilot.
Use the following CRM deal context to answer the question accurately and concisely.
If the answer cannot be determined from the context, say so clearly — do not speculate.

Context:
{context}

Question: {question}

Answer:"""

_PROMPT = PromptTemplate(
    template=_PROMPT_TEMPLATE,
    input_variables=["context", "question"],
)

# ---------------------------------------------------------------------------
# Chain factory
# ---------------------------------------------------------------------------

_RETRIEVER_SEARCH_KWARGS: dict = {"k": 5}


def _build_chain() -> RetrievalQA:
    """Construct the RetrievalQA chain from the persisted vector store."""
    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=_RETRIEVER_SEARCH_KWARGS,
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

    logger.info("RAG query received: %r", question)

    chain = _build_chain()
    result: dict = chain.invoke({"query": question})
    answer: str = result.get("result", "").strip()

    logger.info("RAG answer generated (%d chars).", len(answer))
    return answer