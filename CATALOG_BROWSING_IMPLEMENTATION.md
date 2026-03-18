# Catalog Browsing Implementation Plan

## Overview

Catalog browsing enables users to explore comic collections hierarchically (publisher → series → issues) rather than searching for specific issues. This feature is essential for:

- **Discovery**: Browsing publishers to find new series
- **Collection building**: Viewing all issues in a series before importing
- **Research**: Exploring publisher catalogs chronologically
- **User experience**: Familiar browse pattern from other comic platforms

## Changes Needed

Add 3 new dataclass models to `longbox_commons/models.py`:

1. **PublisherInfo**: Publisher metadata (name, series count, country, years active)
2. **SeriesBrowseInfo**: Series metadata (title, publisher, years, issue count)
3. **IssueInfo**: Issue metadata (number, title, cover date, variants)

**Note**: Named `SeriesBrowseInfo` to avoid conflict with the existing `SeriesInfo` Pydantic model in `models.py` (line 13).

## Code to Add

Add the following imports at the top of `longbox_commons/models.py` (if not already present):

```python
from dataclasses import dataclass
from typing import Optional
```

Then add these 3 dataclass models at the end of `longbox_commons/models.py`:

```python
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
```

Add these exports to `longbox_commons/__init__.py`:

```python
from longbox_commons.models import (
    # Existing exports...
    PublisherInfo,
    SeriesBrowseInfo,
    IssueInfo,
)

__all__ = [
    # Existing exports...
    "PublisherInfo",
    "SeriesBrowseInfo",
    "IssueInfo",
]
```

## Testing

### Unit Tests

Create `tests/test_catalog_models.py`:

```python
import pytest
from datetime import date
from longbox_commons.models import PublisherInfo, SeriesBrowseInfo, IssueInfo


def test_publisher_info_creation():
    publisher = PublisherInfo(
        publisher="marvel",
        name="Marvel Comics",
        series_count=1500,
        country="United States",
        year_began=1939,
        url="https://example.com/publishers/marvel"
    )
    assert publisher.publisher == "marvel"
    assert publisher.year_ended is None


def test_series_browse_info_creation():
    series = SeriesBrowseInfo(
        series_id="amazing-spider-man",
        title="The Amazing Spider-Man",
        publisher="marvel",
        start_year=1963,
        end_year=None,  # Ongoing
        issue_count=900,
        language="en"
    )
    assert series.series_id == "amazing-spider-man"
    assert series.end_year is None


def test_issue_info_creation():
    issue = IssueInfo(
        issue_id="asm-1",
        series_id="amazing-spider-man",
        issue_number="1",
        title="First Appearance",
        cover_date=date(1963, 3, 1),
        price="$0.12",
        page_count=36
    )
    assert issue.issue_number == "1"
    assert issue.variant_of is None


def test_variant_issue_info():
    variant = IssueInfo(
        issue_id="asm-1-variant",
        series_id="amazing-spider-man",
        issue_number="1",
        variant_name="Todd McFarlane Variant",
        variant_of="asm-1"
    )
    assert variant.variant_of == "asm-1"
    assert variant.title is None


def test_optional_fields_all_none():
    """Test that models work with only required fields."""
    publisher = PublisherInfo(publisher="test", name="Test Publisher")
    series = SeriesBrowseInfo(series_id="test", title="Test Series")
    issue = IssueInfo(issue_id="test", series_id="series", issue_number="1")

    assert publisher.series_count is None
    assert series.start_year is None
    assert issue.title is None


def test_immutable_dataclasses():
    """Test that dataclasses are frozen (immutable)."""
    publisher = PublisherInfo(publisher="dc", name="DC Comics")

    with pytest.raises(Exception):  # FrozenInstanceError
        publisher.name = "Updated"


def test_field_naming_consistency():
    """Test that field naming aligns with existing models."""
    series = SeriesBrowseInfo(
        series_id="test",
        title="Test Series",
        publisher="marvel",  # Not publisher_id
        start_year=2020,     # Not year_start
        end_year=2024        # Not year_end
    )

    assert hasattr(series, "publisher")
    assert hasattr(series, "start_year")
    assert hasattr(series, "end_year")
    assert not hasattr(series, "publisher_id")
    assert not hasattr(series, "year_start")
    assert not hasattr(series, "year_end")
```

Run tests with:

```bash
# In longbox-commons directory
pytest tests/test_catalog_models.py -v
```

### Integration Testing

Test that models can be serialized/deserialized:

```python
import json
from dataclasses import asdict

publisher = PublisherInfo(publisher="dc", name="DC Comics")
publisher_dict = asdict(publisher)
publisher_json = json.dumps(publisher_dict)

# Verify JSON round-trip
restored = PublisherInfo(**json.loads(publisher_json))
assert restored.publisher == "dc"
```

## Dependencies

**No new dependencies required.**

These models use only Python standard library:
- `dataclasses` (Python 3.7+)
- `datetime` (standard library)
- `typing` (standard library)

## Backward Compatibility

**This is a purely additive change with no breaking changes.**

- Existing Pydantic models (`SeriesInfo`, `IssueCandidate`, etc.) remain unchanged
- Existing imports continue to work
- New dataclasses can be imported explicitly:

```python
from longbox_commons.models import PublisherInfo, SeriesBrowseInfo, IssueInfo
```

**Naming clarification**: The new model is named `SeriesBrowseInfo` to avoid confusion with the existing `SeriesInfo` Pydantic model.

## Implementation Steps

1. Add the 3 dataclass models to `longbox_commons/models.py`
2. Update `longbox_commons/__init__.py` to export the new models (add to `__all__`)
3. Create `tests/test_catalog_models.py` with unit tests
4. Run `pytest tests/test_catalog_models.py -v` to verify
5. Run full test suite: `pytest` to ensure no regressions

## Key Design Decisions

1. **Immutability**: All dataclasses use `frozen=True` to prevent accidental mutation
2. **Field naming**: Aligns with existing models (`publisher`, `start_year`, `end_year`)
3. **Class naming**: `SeriesBrowseInfo` avoids conflict with existing `SeriesInfo` Pydantic model
4. **Explicit exports**: Added to `__all__` for clear public API

## Next Steps

After implementing these models, they can be used in:

- Platform adapters to return catalog browse results
- API endpoints for catalog browsing (e.g., `/api/publishers`, `/api/series/{id}`)
- CLI commands for interactive catalog browsing
- UI components for hierarchical navigation
