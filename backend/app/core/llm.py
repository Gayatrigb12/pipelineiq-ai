# # from functools import lru_cache

# # from langchain_openai import ChatOpenAI

# # from app.core.config import Settings, get_settings


# # def build_llm(settings: Settings | None = None) -> ChatOpenAI:
# #     """
# #     Construct and return a ChatOpenAI instance.

# #     Args:
# #         settings: Optional Settings override (useful in tests).

# #     Returns:
# #         A configured ChatOpenAI instance.
# #     """
# #     cfg = settings or get_settings()

# #     return ChatOpenAI(
# #         api_key=cfg.openai_api_key_str,
# #         model="gpt-4o-mini",
# #         temperature=0.0,
# #         streaming=False,
# #     )


# # @lru_cache(maxsize=1)
# # def get_llm() -> ChatOpenAI:
# #     """
# #     Return a cached, application-scoped ChatOpenAI singleton.

# #     Use this in FastAPI dependency injection or module-level imports
# #     where a shared instance is desirable.
# #     """
# #     return build_llm()

# from functools import lru_cache

# from langchain_groq import ChatGroq
# from app.core.config import get_settings, Settings


# def build_llm(settings: Settings | None = None) -> ChatGroq:
#     cfg = settings or get_settings()

#     return ChatGroq(
#         groq_api_key=cfg.groq_api_key_str,
#         model="llama3-70b-8192",
#         temperature=0.0,
#     )


# @lru_cache(maxsize=1)
# def get_llm() -> ChatGroq:
#     return build_llm()

from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import Settings, get_settings


def build_llm(settings: Settings | None = None) -> ChatGroq:
    """
    Construct and return a ChatGroq instance.

    Args:
        settings: Optional Settings override (useful in tests).

    Returns:
        A configured ChatGroq instance.
    """
    cfg = settings or get_settings()

    return ChatGroq(
        api_key=cfg.groq_api_key_str,
        model=cfg.groq_model,
        temperature=0.0,
        streaming=False,
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """
    Return a cached, application-scoped ChatGroq singleton.

    Use this in FastAPI dependency injection or module-level imports
    where a shared instance is desirable.
    """
    return build_llm()