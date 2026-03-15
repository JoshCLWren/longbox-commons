"""Tests for longbox_commons.models."""

from datetime import date

from longbox_commons.models import (
    ComicIdentity,
    IssueCandidate,
    SeriesCandidate,
    SeriesInfo,
)


class TestSeriesInfo:
    """SeriesInfo model."""

    def test_minimal(self) -> None:
        """Test SeriesInfo with minimal required fields."""
        s = SeriesInfo(title="X-Men")
        assert s.title == "X-Men"
        assert s.start_year is None

    def test_full(self) -> None:
        """Test SeriesInfo with all optional fields populated."""
        s = SeriesInfo(
            title="X-Men",
            start_year=1963,
            publisher="Marvel",
            end_year=1981,
            volume_number=1,
        )
        assert s.publisher == "Marvel"
        assert s.volume_number == 1

    def test_frozen(self) -> None:
        """Test that SeriesInfo is frozen and immutable."""
        s = SeriesInfo(title="X-Men")
        try:
            s.title = "New X-Men"
            raised = False
        except Exception:
            raised = True
        assert raised


class TestIssueCandidate:
    """IssueCandidate model."""

    def test_display_issue_number_plain(self) -> None:
        """Test display_issue_number with plain issue number."""
        ic = IssueCandidate(
            source="clz",
            source_series_id="xmen",
            source_issue_id="123",
            series_title="X-Men",
            issue_number="1",
        )
        assert ic.display_issue_number() == "1"

    def test_display_issue_number_with_variant(self) -> None:
        """Test display_issue_number with variant suffix."""
        ic = IssueCandidate(
            source="clz",
            source_series_id="xmen",
            source_issue_id="123",
            series_title="X-Men",
            issue_number="1",
            variant_suffix="A",
        )
        assert ic.display_issue_number() == "1.A"

    def test_optional_fields(self) -> None:
        """Test IssueCandidate with optional fields populated."""
        ic = IssueCandidate(
            source="gcd",
            source_series_id="100",
            source_issue_id="200",
            series_title="Batman",
            issue_number="42",
            cover_date=date(1990, 6, 1),
            price=1.50,
            upc="123456789",
        )
        assert ic.cover_date == date(1990, 6, 1)
        assert ic.price == 1.50
        assert ic.upc == "123456789"


class TestSeriesCandidate:
    """SeriesCandidate model."""

    def test_minimal(self) -> None:
        """Test SeriesCandidate with minimal required fields."""
        sc = SeriesCandidate(
            source="clz",
            source_series_id="batman",
            series_title="Batman",
        )
        assert sc.series_title == "Batman"
        assert sc.publisher is None

    def test_with_publisher(self) -> None:
        """Test SeriesCandidate with publisher field populated."""
        sc = SeriesCandidate(
            source="gcd",
            source_series_id="42",
            series_title="Justice League",
            series_start_year=1987,
            publisher="DC",
        )
        assert sc.publisher == "DC"
        assert sc.series_start_year == 1987


class TestComicIdentity:
    """ComicIdentity model."""

    def test_creation(self) -> None:
        """Test ComicIdentity creation with all fields."""
        ci = ComicIdentity(
            series_title="Doom Patrol",
            issue_number="19",
            publisher="DC",
            year=1989,
            overall_confidence=0.95,
            explanation="Exact match on series+issue+year",
        )
        assert ci.overall_confidence == 0.95
        assert ci.explanation == "Exact match on series+issue+year"

    def test_frozen(self) -> None:
        """Test that ComicIdentity is frozen and immutable."""
        ci = ComicIdentity(series_title="X", issue_number="1")
        try:
            ci.series_title = "Y"
            raised = False
        except Exception:
            raised = True
        assert raised
