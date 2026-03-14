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
        s = SeriesInfo(title="X-Men")
        assert s.title == "X-Men"
        assert s.start_year is None

    def test_full(self) -> None:
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
        ic = IssueCandidate(
            source="clz",
            source_series_id="xmen",
            source_issue_id="123",
            series_title="X-Men",
            issue_number="1",
        )
        assert ic.display_issue_number() == "1"

    def test_display_issue_number_with_variant(self) -> None:
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
        sc = SeriesCandidate(
            source="clz",
            source_series_id="batman",
            series_title="Batman",
        )
        assert sc.series_title == "Batman"
        assert sc.publisher is None

    def test_with_publisher(self) -> None:
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
        ci = ComicIdentity(series_title="X", issue_number="1")
        try:
            ci.series_title = "Y"
            raised = False
        except Exception:
            raised = True
        assert raised
