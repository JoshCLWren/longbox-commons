"""Comic domain models.

Pydantic models for representing comic series, issues, and identity
candidates across platforms.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict


class SeriesInfo(BaseModel):
    """Core series metadata shared across platforms."""

    model_config = ConfigDict(frozen=True)

    title: str
    start_year: int | None = None
    publisher: str | None = None
    end_year: int | None = None
    volume_number: int | None = None


class IssueCandidate(BaseModel):
    """Intermediate issue representation from a source platform.

    Not the canonical issue entity — a candidate to be reconciled
    against the canonical database during ingestion.
    """

    source: str
    source_series_id: str
    source_issue_id: str

    series_title: str
    series_start_year: int | None = None
    publisher: str | None = None

    issue_number: str
    variant_suffix: str | None = None

    cover_date: date | None = None
    publication_date: date | None = None
    price: float | None = None
    page_count: int | None = None
    upc: str | None = None
    isbn: str | None = None
    variant_name: str | None = None

    raw_payload: dict[str, str] | None = None

    def display_issue_number(self) -> str:
        """Issue number with variant suffix for display."""
        if self.variant_suffix:
            return f"{self.issue_number}.{self.variant_suffix}"
        return self.issue_number


class SeriesCandidate(BaseModel):
    """Intermediate series representation from a source platform."""

    source: str
    source_series_id: str

    series_title: str
    series_start_year: int | None = None
    publisher: str | None = None
    series_end_year: int | None = None
    volume_number: int | None = None

    raw_payload: dict[str, str] | None = None


class ComicIdentity(BaseModel):
    """Resolved comic identity with confidence metadata."""

    model_config = ConfigDict(frozen=True)

    series_title: str
    issue_number: str
    publisher: str | None = None
    year: int | None = None
    variant_suffix: str | None = None

    issue_confidence: float = 0.0
    variant_confidence: float = 0.0
    overall_confidence: float = 0.0
    explanation: str = ""
