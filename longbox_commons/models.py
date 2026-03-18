"""Comic domain models.

Pydantic models for representing comic series, issues, and identity
candidates across platforms.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


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

    raw_payload: dict[str, Any] | None = Field(default=None)

    def display_issue_number(self) -> str:
        """Issue number with variant suffix for display."""
        if self.variant_suffix:
            return f"{self.issue_number}.{self.variant_suffix}"
        return self.issue_number


class PublisherCandidate(BaseModel):
    """Intermediate publisher representation from a source platform."""

    source: str
    source_publisher_id: str
    publisher_name: str
    raw_payload: dict[str, Any] | None = Field(default=None)


class SeriesCandidate(BaseModel):
    """Intermediate series representation from a source platform."""

    source: str
    source_series_id: str

    series_title: str
    series_start_year: int | None = None
    publisher: str | None = None
    series_end_year: int | None = None
    volume_number: int | None = None

    raw_payload: dict[str, Any] | None = Field(default=None)


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


@dataclass(frozen=True)
class PublisherInfo:
    """Publisher metadata from catalog browsing.

    Represents a publisher in a hierarchical catalog browse operation.
    Used for displaying publisher lists and publisher detail pages.

    Attributes:
        publisher: Unique identifier from the source platform
        name: Publisher name (e.g., "Marvel", "DC Comics")
        series_count: Total number of series for this publisher
        country: Country of origin (e.g., "United States")
        year_began: Year publisher was founded
        year_ended: Year publisher ceased operations (None if still active)
        url: Platform URL for this publisher
    """

    publisher: str
    name: str
    series_count: Optional[int] = None
    country: Optional[str] = None
    year_began: Optional[int] = None
    year_ended: Optional[int] = None
    url: Optional[str] = None


@dataclass(frozen=True)
class SeriesBrowseInfo:
    """Series metadata from catalog browsing.

    Represents a comic series in a hierarchical catalog browse operation.
    Used for displaying series lists under a publisher and series detail pages.

    Attributes:
        series_id: Unique identifier from the source platform
        title: Series title (e.g., "The Amazing Spider-Man")
        publisher: Parent publisher identifier
        start_year: Year series began publication
        end_year: Year series ended (None if ongoing)
        issue_count: Total number of issues
        country: Country of publication
        language: Primary language (e.g., "en", "fr")
        url: Platform URL for this series
    """

    series_id: str
    title: str
    publisher: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    issue_count: Optional[int] = None
    country: Optional[str] = None
    language: Optional[str] = None
    url: Optional[str] = None


@dataclass(frozen=True)
class IssueInfo:
    """Issue metadata from catalog browsing.

    Represents a single comic issue in a hierarchical catalog browse operation.
    Used for displaying issue lists under a series.

    Attributes:
        issue_id: Unique identifier from the source platform
        series_id: Parent series identifier
        issue_number: Issue number (stored as string to support "-1", "1/2", etc.)
        title: Issue title (optional, many issues don't have titles)
        variant_name: Variant description (e.g., "Variant Cover", "Newsstand")
        cover_date: Cover date (month/year on the cover)
        price: Cover price (as string, e.g., "$2.99", "£1.50")
        page_count: Number of pages
        variant_of: If this is a variant, the issue_id of the base issue
        url: Platform URL for this issue
    """

    issue_id: str
    series_id: str
    issue_number: str
    title: Optional[str] = None
    variant_name: Optional[str] = None
    cover_date: Optional[date] = None
    price: Optional[str] = None
    page_count: Optional[int] = None
    variant_of: Optional[str] = None
    url: Optional[str] = None
