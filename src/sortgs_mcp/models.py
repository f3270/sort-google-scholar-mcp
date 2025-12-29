"""Pydantic models for data validation and serialization."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class Paper(BaseModel):
    """Represents a research paper from Google Scholar."""

    rank: int = Field(..., description="Rank in search results")
    title: str = Field(..., description="Paper title")
    authors: str = Field(..., description="Author string")
    citations: int = Field(..., description="Number of citations")
    year: int = Field(..., description="Publication year")
    publisher: str = Field(..., description="Publisher string")
    venue: str = Field(..., description="Venue/journal")
    content_snippet: str = Field(..., description="Content preview/abstract snippet")
    source_url: str = Field(..., description="URL to paper source")
    pdf_url: str | None = Field(None, description="Direct PDF link if available")
    cit_per_year: int = Field(..., description="Citations per year (calculated)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rank": 1,
                "title": "Attention Is All You Need",
                "authors": "A Vaswani, N Shazeer, N Parmar, J Uszkoreit, ...",
                "citations": 95000,
                "year": 2017,
                "publisher": "Curran Associates, Inc.",
                "venue": "Advances in neural information processing systems",
                "content_snippet": "The dominant sequence transduction models...",
                "source_url": "https://arxiv.org/abs/1706.03762",
                "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                "cit_per_year": 11875,
            }
        }


class SearchParams(BaseModel):
    """Parameters for a Google Scholar search."""

    keywords: str = Field(..., description="Search query keywords")
    num_results: int = Field(default=100, ge=10, le=1000, description="Number of results to fetch")
    sort_by: Literal["Citations", "cit/year"] = Field(
        default="Citations",
        description="Column to sort results by",
    )
    start_year: int | None = Field(None, ge=1900, le=2100, description="Filter papers from this year onwards")
    end_year: int | None = Field(None, ge=1900, le=2100, description="Filter papers up to this year")
    languages: list[str] | None = Field(None, description="Language filter codes (e.g., ['en', 'es'])")
    debug: bool = Field(default=False, description="Debug mode (uses web archive)")

    @model_validator(mode="after")
    def validate_year_range(self) -> "SearchParams":
        """Ensure start_year is not greater than end_year when both are set."""
        if self.start_year is not None and self.end_year is not None:
            if self.start_year > self.end_year:
                raise ValueError(
                    f"start_year ({self.start_year}) must be <= end_year ({self.end_year})"
                )
        return self

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "keywords": "machine learning transformers",
                "num_results": 100,
                "sort_by": "cit/year",
                "start_year": 2017,
                "end_year": 2024,
                "languages": ["en"],
                "debug": False,
            }
        }


class DownloadMetadata(BaseModel):
    """Metadata for a single downloaded PDF."""

    rank: int = Field(..., description="Paper rank in search results")
    title: str = Field(..., description="Paper title")
    pdf_path: str = Field(..., description="Relative path to PDF file")
    file_size_bytes: int = Field(..., description="PDF file size in bytes")
    download_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the PDF was downloaded",
    )
    status: Literal["downloaded", "skipped"] = Field(
        default="downloaded",
        description="Download status for the PDF",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rank": 1,
                "title": "Attention Is All You Need",
                "pdf_path": "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                "file_size_bytes": 1234567,
                "download_timestamp": "2025-12-29T16:15:00",
                "status": "downloaded",
            }
        }


class SearchSession(BaseModel):
    """Represents a complete search session with results."""

    session_id: str = Field(..., description="Unique session identifier (UUID)")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    params: SearchParams = Field(..., description="Search parameters used")
    papers: list[Paper] = Field(default_factory=list, description="Found papers")
    papers_count: int = Field(default=0, description="Total number of papers found")
    pdfs_downloaded: int = Field(default=0, description="Number of PDFs downloaded")
    download_metadata: list[DownloadMetadata] = Field(
        default_factory=list,
        description="Metadata for downloaded PDFs",
    )
    indexed: bool = Field(default=False, description="Whether papers have been indexed in vector DB")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2025-01-15T10:30:00",
                "params": {
                    "keywords": "transformers attention mechanism",
                    "num_results": 50,
                    "sort_by": "Citations",
                },
                "papers": [],
                "papers_count": 50,
                "pdfs_downloaded": 10,
                "indexed": True,
            }
        }


class PDFDownloadResult(BaseModel):
    """Result of PDF download operation."""

    session_id: str = Field(..., description="Session ID")
    downloaded: int = Field(..., description="Number of successfully downloaded PDFs")
    skipped: int = Field(default=0, description="Number of PDFs skipped due to existing valid files")
    failed: int = Field(..., description="Number of failed downloads")
    pdf_paths: list[str] = Field(default_factory=list, description="Paths to downloaded PDFs")
    failed_papers: list[dict] = Field(default_factory=list, description="Papers that failed to download")
    download_metadata: list["DownloadMetadata"] = Field(
        default_factory=list,
        description="Detailed metadata for each downloaded PDF",
    )
    error: str | None = Field(
        default=None,
        description="Error message if batch operation failed before processing",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "downloaded": 8,
                "skipped": 0,
                "failed": 2,
                "pdf_paths": [
                    "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                    "data/sessions/550e.../pdfs/paper_002_bert.pdf",
                ],
                "failed_papers": [
                    {"rank": 3, "title": "...", "reason": "403 Forbidden"}
                ],
                "download_metadata": [
                    {
                        "rank": 1,
                        "title": "Attention Is All You Need",
                        "pdf_path": "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                        "file_size_bytes": 1234567,
                        "download_timestamp": "2025-12-29T16:15:00",
                        "status": "downloaded",
                    }
                ],
                "error": None,
            }
        }




class IndexingResult(BaseModel):
    """Result of indexing operation."""

    session_id: str = Field(..., description="Session ID")
    papers_indexed: int = Field(..., description="Number of papers successfully indexed")
    chunks_created: int = Field(..., description="Total number of chunks created")
    indexing_time_sec: float = Field(..., description="Time taken for indexing in seconds")
    failed_papers: list[str] = Field(default_factory=list, description="Paper titles that failed to index")


class QuerySource(BaseModel):
    """A source chunk returned from RAG query."""

    paper_title: str = Field(..., description="Title of the source paper")
    chunk_text: str = Field(..., description="Relevant text chunk")
    relevance_score: float = Field(..., description="Similarity/relevance score")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class QueryResult(BaseModel):
    """Result of RAG query operation."""

    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Generated answer from RAG")
    sources: list[QuerySource] = Field(default_factory=list, description="Source chunks used")
    session_id: str | None = Field(None, description="Session ID if scoped")
