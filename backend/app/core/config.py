# from functools import lru_cache
# from pathlib import Path

# from pydantic import Field, SecretStr
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     """Application settings loaded from environment variables / .env file."""

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=False,
#         extra="ignore",
#     )

#     # ------------------------------------------------------------------
#     # OpenAI
#     # ------------------------------------------------------------------
#     # openai_api_key: SecretStr = Field(..., alias="OPENAI_API_KEY")
#     groq_api_key: SecretStr = Field(..., alias="GROQ_API_KEY")

#     # ------------------------------------------------------------------
#     # ChromaDB
#     # ------------------------------------------------------------------
#     chroma_db_path: Path = Field(
#         default=Path("chroma_db"),
#         alias="CHROMA_DB_PATH",
#     )

#     # ------------------------------------------------------------------
#     # Helpers
#     # ------------------------------------------------------------------

#     @property
#     def openai_api_key_str(self) -> str:
#         """Return the raw API key string (use only where a plain str is required)."""
#         return self.openai_api_key.get_secret_value()

# @property
# def groq_api_key_str(self) -> str:
#     return self.groq_api_key.get_secret_value()

# @lru_cache(maxsize=1)
# def get_settings() -> Settings:
#     """Return a cached singleton Settings instance."""
#     return Settings()

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Groq
    # ------------------------------------------------------------------
    groq_api_key: SecretStr = Field(..., alias="GROQ_API_KEY")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_MODEL",
    )

    # ------------------------------------------------------------------
    # ChromaDB
    # ------------------------------------------------------------------
    chroma_db_path: Path = Field(
        default=Path("chroma_db"),
        alias="CHROMA_DB_PATH",
    )

    # ------------------------------------------------------------------
    # HuggingFace Embeddings
    # ------------------------------------------------------------------
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL_NAME",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def groq_api_key_str(self) -> str:
        """Return the raw Groq API key string (use only where a plain str is required)."""
        return self.groq_api_key.get_secret_value()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()