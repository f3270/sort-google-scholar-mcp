"""Configuration management using pydantic-settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for LLM integration (optional for MCP server startup)",
    )

    # Data directories
    data_dir: Path = Field(
        default=Path("./data"),
        description="Root directory for all data storage",
    )

    @property
    def sessions_dir(self) -> Path:
        """Directory for search sessions."""
        return self.data_dir / "sessions"

    @property
    def chroma_persist_dir(self) -> Path:
        """Directory for ChromaDB persistence."""
        return self.data_dir / "vectorstore"

    def pdf_download_dir(self, session_id: str) -> Path:
        """Directory for PDF downloads for a session."""
        return self.sessions_dir / session_id / "pdfs"

    # Embedding configuration
    embedding_model: str = Field(
        default="all-mpnet-base-v2",
        description="Sentence-transformers model for embeddings",
    )

    # LLM configuration
    openai_model_keywords: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for keyword generation (cheap/fast)",
    )

    openai_model_rag: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for RAG question answering (quality)",
    )

    # PDF processing
    max_concurrent_downloads: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent PDF downloads",
    )

    chunk_size: int = Field(
        default=1000,
        description="Default chunk size for text splitting",
    )

    chunk_overlap: int = Field(
        default=200,
        description="Default overlap between chunks",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    def model_post_init(self, __context) -> None:
        """Create data directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
