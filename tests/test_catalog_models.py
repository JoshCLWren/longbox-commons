"""Tests for catalog browsing models."""

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
        url="https://example.com/publishers/marvel",
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
        language="en",
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
        page_count=36,
    )
    assert issue.issue_number == "1"
    assert issue.variant_of is None


def test_variant_issue_info():
    variant = IssueInfo(
        issue_id="asm-1-variant",
        series_id="amazing-spider-man",
        issue_number="1",
        variant_name="Todd McFarlane Variant",
        variant_of="asm-1",
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
        start_year=2020,  # Not year_start
        end_year=2024,  # Not year_end
    )

    assert hasattr(series, "publisher")
    assert hasattr(series, "start_year")
    assert hasattr(series, "end_year")
    assert not hasattr(series, "publisher_id")
    assert not hasattr(series, "year_start")
    assert not hasattr(series, "year_end")
