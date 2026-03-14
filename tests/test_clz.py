"""Tests for longbox_commons.clz — CLZ CSV read/write and row mapping."""

import tempfile
from pathlib import Path

import pytest

from longbox_commons.clz import (
    CLZValidationError,
    read_csv_file,
    read_csv_string,
    row_to_issue,
    row_to_series,
    write_csv_file,
)

MINIMAL_CSV = (
    "Series,Issue,Publisher,Core ComicID,Year\n"
    "X-Men,1,Marvel,12345,1963\n"
)

MULTI_ROW_CSV = (
    "Series,Issue,Publisher,Core ComicID,Year\n"
    "X-Men,1,Marvel,12345,1963\n"
    "Batman,42,DC,67890,1990\n"
)


class TestReadCSV:
    """CSV reading from file and string."""

    def test_read_string(self) -> None:
        rows = read_csv_string(MINIMAL_CSV)
        assert len(rows) == 1
        assert rows[0]["Series"] == "X-Men"

    def test_read_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(MINIMAL_CSV, encoding="utf-8")
        rows = read_csv_file(csv_file)
        assert len(rows) == 1

    def test_read_bom(self) -> None:
        rows = read_csv_string("\ufeff" + MINIMAL_CSV)
        assert len(rows) == 1

    def test_empty_string_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="empty"):
            read_csv_string("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="empty"):
            read_csv_string("   ")

    def test_headers_only_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="no data"):
            read_csv_string("Series,Issue,Publisher\n")

    def test_file_not_found(self) -> None:
        with pytest.raises(CLZValidationError, match="not found"):
            read_csv_file("/nonexistent/path.csv")

    def test_encoding_error(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.csv"
        bad_file.write_bytes(b"\x80\x81\x82\x83")
        with pytest.raises(CLZValidationError, match="encoding"):
            read_csv_file(bad_file)

    def test_multi_row(self) -> None:
        rows = read_csv_string(MULTI_ROW_CSV)
        assert len(rows) == 2
        assert rows[1]["Series"] == "Batman"


class TestWriteCSV:
    """CSV writing."""

    def test_write_and_read_back(self, tmp_path: Path) -> None:
        rows = [
            {"Series": "X-Men", "Issue": "1"},
            {"Series": "Batman", "Issue": "42"},
        ]
        out = tmp_path / "out.csv"
        write_csv_file(rows, out)
        result = read_csv_file(out)
        assert len(result) == 2
        assert result[0]["Series"] == "X-Men"

    def test_empty_rows_no_file(self, tmp_path: Path) -> None:
        out = tmp_path / "empty.csv"
        write_csv_file([], out)
        assert not out.exists()


class TestRowToSeries:
    """CSV row → SeriesCandidate."""

    def test_basic(self) -> None:
        row = {"Series": "X-Men", "Publisher": "Marvel", "Year": "1963"}
        sc = row_to_series("x-men-v1", row)
        assert sc.series_title == "X-Men"
        assert sc.publisher == "Marvel"
        assert sc.series_start_year == 1963
        assert sc.source == "clz"

    def test_empty_row_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="empty"):
            row_to_series("id", {})

    def test_missing_series_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="Series"):
            row_to_series("id", {"Publisher": "Marvel"})

    def test_fallback_year_columns(self) -> None:
        row = {"Series": "Batman", "Cover Year": "1990"}
        sc = row_to_series("batman", row)
        assert sc.series_start_year == 1990


class TestRowToIssue:
    """CSV row → IssueCandidate."""

    def test_basic(self) -> None:
        row = {
            "Series": "X-Men",
            "Issue": "1",
            "Publisher": "Marvel",
            "Core ComicID": "12345",
            "Year": "1963",
        }
        ic = row_to_issue(row)
        assert ic.series_title == "X-Men"
        assert ic.issue_number == "1"
        assert ic.source == "clz"

    def test_variant_suffix(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1A",
            "Publisher": "DC",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "1"
        assert ic.variant_suffix == "A"

    def test_empty_row_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="empty"):
            row_to_issue({})

    def test_missing_comic_id_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="Core ComicID"):
            row_to_issue({"Series": "X-Men", "Issue": "1"})

    def test_missing_series_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="Series"):
            row_to_issue({"Issue": "1", "Core ComicID": "123"})

    def test_nn_issue_defaults_to_one(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "NN",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "1"

    def test_nn_with_issue_nr_column(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "NN",
            "Issue Nr": "5",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "5"

    def test_format_code_as_issue(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "TP",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "1"
        assert ic.variant_suffix == "TP"

    def test_missing_issue_with_format(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "",
            "Format": "Trade Paperback",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "1"

    def test_missing_issue_no_format_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="Issue"):
            row_to_issue({
                "Series": "Batman",
                "Issue": "",
                "Core ComicID": "99",
            })

    def test_unicode_fraction(self) -> None:
        row = {
            "Series": "X-Men",
            "Issue": "½",
            "Core ComicID": "99",
        }
        ic = row_to_issue(row)
        assert ic.issue_number == "1/2"

    def test_cover_date_parsing(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Cover Date": "May 21, 1997",
        }
        ic = row_to_issue(row)
        assert ic.cover_date is not None
        assert ic.cover_date.year == 1997

    def test_price_parsing(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Price": "$2.99",
        }
        ic = row_to_issue(row)
        assert ic.price == 2.99

    def test_upc_cleaning(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Barcode": "123 456 789",
        }
        ic = row_to_issue(row)
        assert ic.upc == "123456789"

    def test_variant_name(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1A",
            "Core ComicID": "99",
            "Variant Description": "Jim Lee Cover",
        }
        ic = row_to_issue(row)
        assert ic.variant_name == "Jim Lee Cover"

    def test_invalid_issue_number_raises(self) -> None:
        with pytest.raises(CLZValidationError, match="Invalid issue"):
            row_to_issue({
                "Series": "Batman",
                "Issue": "X-Men -1",
                "Core ComicID": "99",
            })

    def test_invalid_year_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Year": "not-a-year",
        }
        ic = row_to_issue(row)
        assert ic.series_start_year is None

    def test_year_out_of_range_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Year": "1700",
        }
        ic = row_to_issue(row)
        assert ic.series_start_year is None

    def test_unparseable_date_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Cover Date": "not-a-date",
        }
        ic = row_to_issue(row)
        assert ic.cover_date is None

    def test_whitespace_only_date_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Cover Date": "   ",
        }
        ic = row_to_issue(row)
        assert ic.cover_date is None

    def test_unparseable_price_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Price": "free",
        }
        ic = row_to_issue(row)
        assert ic.price is None

    def test_page_count_non_digit(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Pages": "unknown",
        }
        ic = row_to_issue(row)
        assert ic.page_count is None

    def test_upc_non_digit_returns_none(self) -> None:
        row = {
            "Series": "Batman",
            "Issue": "1",
            "Core ComicID": "99",
            "Barcode": "ABC-XYZ",
        }
        ic = row_to_issue(row)
        assert ic.upc is None
