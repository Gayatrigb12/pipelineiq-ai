# # # from __future__ import annotations

# # # import logging
# # # from pathlib import Path
# # # from typing import Sequence

# # # # from langchain_chroma import Chroma
# # # from langchain_community.vectorstores import Chroma
# # # from langchain_core.documents import Document
# # # # from langchain_openai import OpenAIEmbeddings
# # # from langchain_huggingface import HuggingFaceEmbeddings

# # # from app.core.config import get_settings

# # # logger = logging.getLogger(__name__)

# # # # ---------------------------------------------------------------------------
# # # # Internal helpers
# # # # ---------------------------------------------------------------------------

# # # _COLLECTION_NAME = "rag_collection"


# # # def _build_embeddings() -> HuggingFaceEmbeddings:
# # #     """Instantiate HuggingFaceEmbeddings."""
# # #     return HuggingFaceEmbeddings(
# # #         model_name="sentence-transformers/all-MiniLM-L6-v2"
# # #     )

# # #     )


# # # def _resolve_persist_dir(path: Path | str | None = None) -> str:
# # #     """Return the ChromaDB persistence directory as a string."""
# # #     if path is not None:
# # #         return str(path)
# # #     return str(get_settings().chroma_db_path)


# # # # ---------------------------------------------------------------------------
# # # # Public API
# # # # ---------------------------------------------------------------------------


# # # def create_vectorstore(
# # #     documents: Sequence[Document],
# # #     persist_directory: Path | str | None = None,
# # # ) -> Chroma:
# # #     """
# # #     Embed *documents* and persist a new Chroma vector store to disk.

# # #     Args:
# # #         documents:          LangChain Document objects to index.
# # #         persist_directory:  Override for the storage path. Defaults to
# # #                             ``Settings.chroma_db_path``.

# # #     Returns:
# # #         A ready-to-query :class:`Chroma` instance.
# # #     """
# # #     persist_dir = _resolve_persist_dir(persist_directory)
# # #     embeddings = _build_embeddings()

# # #     logger.info(
# # #         "Creating vector store with %d document(s) at '%s'.",
# # #         len(documents),
# # #         persist_dir,
# # #     )

# # #     vectorstore = Chroma.from_documents(
# # #         documents=list(documents),
# # #         embedding=embeddings,
# # #         collection_name=_COLLECTION_NAME,
# # #         persist_directory=persist_dir,
# # #     )

# # #     logger.info("Vector store created and persisted successfully.")
# # #     return vectorstore


# # # def load_vectorstore(
# # #     persist_directory: Path | str | None = None,
# # # ) -> Chroma:
# # #     """
# # #     Load an existing Chroma vector store from disk.

# # #     Args:
# # #         persist_directory:  Override for the storage path. Defaults to
# # #                             ``Settings.chroma_db_path``.

# # #     Returns:
# # #         A ready-to-query :class:`Chroma` instance.

# # #     Raises:
# # #         FileNotFoundError: If *persist_directory* does not exist.
# # #     """
# # #     persist_dir = _resolve_persist_dir(persist_directory)

# # #     if not Path(persist_dir).exists():
# # #         raise FileNotFoundError(
# # #             f"ChromaDB persist directory not found: '{persist_dir}'. "
# # #             "Run create_vectorstore() first."
# # #         )

# # #     embeddings = _build_embeddings()

# # #     logger.info("Loading vector store from '%s'.", persist_dir)

# # #     vectorstore = Chroma(
# # #         collection_name=_COLLECTION_NAME,
# # #         embedding_function=embeddings,
# # #         persist_directory=persist_dir,
# # #     )

# # #     logger.info("Vector store loaded successfully.")
# # #     return vectorstore



# # from __future__ import annotations

# # import logging
# # from pathlib import Path
# # from typing import Sequence

# # from langchain_community.vectorstores import Chroma
# # from langchain_core.documents import Document

# # from app.core.config import get_settings

# # logger = logging.getLogger(__name__)

# # _COLLECTION_NAME = "rag_collection"


# # def _build_embeddings():
# #     from langchain_huggingface import HuggingFaceEmbeddings

# #     return HuggingFaceEmbeddings(
# #         model_name="sentence-transformers/all-MiniLM-L6-v2"
# #     )


# # def _resolve_persist_dir(path: Path | str | None = None) -> str:
# #     if path is not None:
# #         return str(path)
# #     return str(get_settings().chroma_db_path)


# # def create_vectorstore(
# #     documents: Sequence[Document],
# #     persist_directory: Path | str | None = None,
# # ) -> Chroma:

# #     persist_dir = _resolve_persist_dir(persist_directory)
# #     embeddings = _build_embeddings()

# #     vectorstore = Chroma.from_documents(
# #         documents=list(documents),
# #         embedding=embeddings,
# #         collection_name=_COLLECTION_NAME,
# #         persist_directory=persist_dir,
# #     )

# #     return vectorstore


# # def load_vectorstore(
# #     persist_directory: Path | str | None = None,
# # ) -> Chroma:

# #     persist_dir = _resolve_persist_dir(persist_directory)

# #     if not Path(persist_dir).exists():
# #         raise FileNotFoundError("Vector DB not found. Run ingestion first.")

# #     embeddings = _build_embeddings()

# #     return Chroma(
# #         collection_name=_COLLECTION_NAME,
# #         embedding_function=embeddings,
# #         persist_directory=persist_dir,
# #     )

# from __future__ import annotations

# import logging
# from pathlib import Path
# from typing import Sequence

# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# from langchain_huggingface import HuggingFaceEmbeddings

# from app.core.config import get_settings

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # Internal helpers
# # ---------------------------------------------------------------------------

# _COLLECTION_NAME = "rag_collection"


# def _build_embeddings() -> HuggingFaceEmbeddings:
#     """Instantiate HuggingFaceEmbeddings using the configured model name.

#     HuggingFace embeddings run locally — no API key required.
#     The model is downloaded on first use and cached by sentence-transformers.
#     """
#     cfg = get_settings()
#     return HuggingFaceEmbeddings(
#         model_name=cfg.embedding_model_name,
#         model_kwargs={"device": "cpu"},
#         encode_kwargs={"normalize_embeddings": True},
#     )


# def _resolve_persist_dir(path: Path | str | None = None) -> str:
#     """Return the ChromaDB persistence directory as a string."""
#     if path is not None:
#         return str(path)
#     return str(get_settings().chroma_db_path)


# # ---------------------------------------------------------------------------
# # Public API
# # ---------------------------------------------------------------------------


# def create_vectorstore(
#     documents: Sequence[Document],
#     persist_directory: Path | str | None = None,
# ) -> Chroma:
#     """
#     Embed *documents* and persist a new Chroma vector store to disk.

#     Args:
#         documents:          LangChain Document objects to index.
#         persist_directory:  Override for the storage path. Defaults to
#                             ``Settings.chroma_db_path``.

#     Returns:
#         A ready-to-query :class:`Chroma` instance.
#     """
#     persist_dir = _resolve_persist_dir(persist_directory)
#     embeddings = _build_embeddings()

#     logger.info(
#         "Creating vector store with %d document(s) at '%s'.",
#         len(documents),
#         persist_dir,
#     )

#     vectorstore = Chroma.from_documents(
#         documents=list(documents),
#         embedding=embeddings,
#         collection_name=_COLLECTION_NAME,
#         persist_directory=persist_dir,
#     )

#     logger.info("Vector store created and persisted successfully.")
#     return vectorstore


# def load_vectorstore(
#     persist_directory: Path | str | None = None,
# ) -> Chroma:
#     """
#     Load an existing Chroma vector store from disk.

#     Args:
#         persist_directory:  Override for the storage path. Defaults to
#                             ``Settings.chroma_db_path``.

#     Returns:
#         A ready-to-query :class:`Chroma` instance.

#     Raises:
#         FileNotFoundError: If *persist_directory* does not exist.
#     """
#     persist_dir = _resolve_persist_dir(persist_directory)

#     if not Path(persist_dir).exists():
#         raise FileNotFoundError(
#             f"ChromaDB persist directory not found: '{persist_dir}'. "
#             "Run create_vectorstore() first."
#         )

#     embeddings = _build_embeddings()

#     logger.info("Loading vector store from '%s'.", persist_dir)

#     vectorstore = Chroma(
#         collection_name=_COLLECTION_NAME,
#         embedding_function=embeddings,
#         persist_directory=persist_dir,
#     )

#     logger.info("Vector store loaded successfully.")
#     return vectorstore


from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_COLLECTION_NAME = "rag_collection"


def _build_embeddings() -> HuggingFaceEmbeddings:
    """
    Instantiate HuggingFaceEmbeddings using the configured model name.
    Runs locally — no API key required.
    Model is downloaded on first use and cached by sentence-transformers.
    """
    cfg = get_settings()
    return HuggingFaceEmbeddings(
        model_name=cfg.embedding_model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _resolve_persist_dir(path: Path | str | None = None) -> str:
    """Return the ChromaDB persistence directory as a string."""
    if path is not None:
        return str(path)
    return str(get_settings().chroma_db_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_vectorstore(
    documents: Sequence[Document],
    persist_directory: Path | str | None = None,
) -> Chroma:
    """
    Embed *documents* and persist a new Chroma vector store to disk.

    Args:
        documents:          LangChain Document objects to index.
        persist_directory:  Override for the storage path. Defaults to
                            ``Settings.chroma_db_path``.

    Returns:
        A ready-to-query :class:`Chroma` instance.
    """
    persist_dir = _resolve_persist_dir(persist_directory)
    embeddings = _build_embeddings()

    logger.info(
        "Creating vector store with %d document(s) at '%s'.",
        len(documents),
        persist_dir,
    )

    vectorstore = Chroma.from_documents(
        documents=list(documents),
        embedding=embeddings,
        collection_name=_COLLECTION_NAME,
        persist_directory=persist_dir,
    )

    logger.info("Vector store created and persisted successfully.")
    return vectorstore


def load_vectorstore(
    persist_directory: Path | str | None = None,
) -> Chroma:
    """
    Load an existing Chroma vector store from disk.

    Args:
        persist_directory:  Override for the storage path. Defaults to
                            ``Settings.chroma_db_path``.

    Returns:
        A ready-to-query :class:`Chroma` instance.

    Raises:
        FileNotFoundError: If *persist_directory* does not exist.
    """
    persist_dir = _resolve_persist_dir(persist_directory)

    if not Path(persist_dir).exists():
        raise FileNotFoundError(
            f"ChromaDB persist directory not found: '{persist_dir}'. "
            "Run create_vectorstore() first."
        )

    embeddings = _build_embeddings()

    logger.info("Loading vector store from '%s'.", persist_dir)

    vectorstore = Chroma(
        collection_name=_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    logger.info("Vector store loaded successfully.")
    return vectorstore