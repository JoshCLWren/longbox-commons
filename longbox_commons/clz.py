"""CLZ CSV import/export utilities.

Read and write CLZ Comic Collector CSV exports. Maps CLZ column names
to internal candidate models.
"""

import csv
import re
from datetime import date, datetime
from io import StringIO
from pathlib import Path

from longbox_commons.models import IssueCandidate, SeriesCandidate
from longbox_commons.parsing import (
    normalize_unicode_symbols,
    parse_format_issue,
    parse_issue_candidate,
)


class CLZValidationError(Exception):
    """Raised when CLZ CSV data fails validation."""


def read_csv_file(file_path: str | Path) -> list[dict[str, str]]:
    """Load a CLZ CSV export file.

    Args:
        file_path: Path to CSV file.

    Returns:
        List of row dictionaries.

    Raises:
        CLZValidationError: If file cannot be read or parsed.
    """
    try:
        with open(file_path, encoding="utf-8-sig") as f:
            return _parse_csv_content(f.read())
    except FileNotFoundError as e:
        raise CLZValidationError(f"CSV file not found: {file_path}") from e
    except UnicodeDecodeError as e:
        raise CLZValidationError(f"CSV file encoding error: {e}") from e


def read_csv_string(csv_content: str) -> list[dict[str, str]]:
    """Load CLZ CSV data from a string.

    Args:
        csv_content: CSV content.

    Returns:
        List of row dictionaries.

    Raises:
        CLZValidationError: If content cannot be parsed.
    """
    return _parse_csv_content(csv_content)


def _parse_csv_content(content: str) -> list[dict[str, str]]:
    """Parse CSV content into row dictionaries."""
    if not content or not content.strip():
        raise CLZValidationError("CSV content is empty")

    try:
        if content.startswith("\ufeff"):
            content = content[1:]

        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        if not rows:
            raise CLZValidationError("CSV contains no data rows")

        return rows
    except csv.Error as e:
        raise CLZValidationError(f"CSV parsing error: {e}") from e


def write_csv_file(
    rows: list[dict[str, str]],
    file_path: str | Path,
    fieldnames: list[str] | None = None,
) -> None:
    """Write rows to a CSV file.

    Args:
        rows: List of row dictionaries.
        file_path: Output file path.
        fieldnames: Column names. Inferred from first row if not provided.
    """
    if not rows:
        return

    if fieldnames is None:
        fieldnames = list(rows[0].keys())

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def row_to_series(source_series_id: str, row: dict[str, str]) -> SeriesCandidate:
    """Convert a CLZ CSV row to a SeriesCandidate.

    Args:
        source_series_id: Series identifier (typically the series title).
        row: CSV row dictionary.

    Returns:
        SeriesCandidate model.

    Raises:
        CLZValidationError: If required fields are missing.
    """
    if not row:
        raise CLZValidationError("CLZ CSV row is empty")

    series_title = _extract_series_title(row)
    if not series_title:
        raise CLZValidationError("CLZ series missing required field: Series")

    publisher = row.get("Publisher")
    year_began = _parse_year(
        row.get("Year") or row.get("Cover Year") or row.get("Release Year")
    )

    return SeriesCandidate(
        source="clz",
        source_series_id=source_series_id,
        series_title=series_title,
        series_start_year=year_began,
        publisher=publisher,
        raw_payload=row,
    )


def row_to_issue(row: dict[str, str]) -> IssueCandidate:
    """Convert a CLZ CSV row to an IssueCandidate.

    Args:
        row: CSV row dictionary.

    Returns:
        IssueCandidate model.

    Raises:
        CLZValidationError: If required fields are missing or issue number is invalid.
    """
    if not row:
        raise CLZValidationError("CLZ CSV row is empty")

    core_comic_id = row.get("Core ComicID")
    if not core_comic_id:
        raise CLZValidationError("CLZ issue missing required field: Core ComicID")
    source_issue_id = str(core_comic_id).strip()

    series_title = _extract_series_title(row)
    if not series_title:
        raise CLZValidationError("CLZ issue missing required field: Series")

    issue_number_raw = (row.get("Issue") or "").strip()

    if re.match(
        r"^(NN|NN-NN|\d+NN(-[A-Za-z0-9]+)*)$", issue_number_raw, re.IGNORECASE
    ):
        issue_nr = (row.get("Issue Nr") or "").strip()
        if issue_nr and issue_nr.isdigit():
            issue_number_raw = issue_nr
        else:
            issue_number_raw = "1"

    if not issue_number_raw:
        fmt = (row.get("Format") or "").strip()
        if fmt:
            issue_number_raw = "1"
        else:
            raise CLZValidationError("CLZ issue missing required field: Issue")

    issue_number_raw = normalize_unicode_symbols(issue_number_raw)

    format_result = parse_format_issue(issue_number_raw.strip())
    if format_result:
        canonical_issue_number, variant_suffix_override = format_result
    else:
        variant_suffix_override = None
        parse_result = parse_issue_candidate(issue_number_raw)
        if not parse_result.success:
            raise CLZValidationError(
                f"Invalid issue number '{issue_number_raw}': {parse_result.error_code}"
            )
        if parse_result.canonical_issue_number is None:
            raise CLZValidationError(
                f"Issue number '{issue_number_raw}' parsed but produced no canonical form"
            )
        canonical_issue_number = parse_result.canonical_issue_number

    publisher = row.get("Publisher")
    year_began = _parse_year(
        row.get("Year") or row.get("Cover Year") or row.get("Release Year")
    )
    cover_date = _parse_date(row.get("Cover Date"))
    publication_date = _parse_date(row.get("Release Date"))
    price = _parse_price(row.get("Price") or row.get("Cover Price"))
    page_count = _parse_page_count(row.get("Pages") or row.get("No. of Pages"))
    upc = _clean_upc(row.get("Barcode") or row.get("UPC"))

    if variant_suffix_override:
        variant_suffix = variant_suffix_override
    else:
        parse_result_for_variant = parse_issue_candidate(issue_number_raw)
        variant_suffix = parse_result_for_variant.variant_suffix

    variant_name = (row.get("Variant Description") or "").strip() or None

    return IssueCandidate(
        source="clz",
        source_series_id=_extract_series_id(row),
        source_issue_id=source_issue_id,
        series_title=series_title,
        series_start_year=year_began,
        publisher=publisher,
        issue_number=canonical_issue_number,
        variant_suffix=variant_suffix,
        variant_name=variant_name,
        cover_date=cover_date,
        publication_date=publication_date,
        price=price,
        page_count=page_count,
        upc=upc,
        raw_payload=row,
    )


def _extract_series_title(row: dict[str, str]) -> str | None:
    """Extract series title from a CSV row."""
    series = row.get("Series")
    if series:
        return series.strip()
    return None


def _extract_series_id(row: dict[str, str]) -> str:
    """Extract series identifier from a CSV row."""
    title = _extract_series_title(row)
    return title if title else ""


def _parse_year(year_str: str | None) -> int | None:
    """Parse a year string, returning None if invalid."""
    if not year_str:
        return None
    try:
        year = int(str(year_str).strip())
        if 1800 <= year <= 2100:
            return year
    except ValueError:
        pass
    return None


def _parse_date(date_str: str | None) -> date | None:
    """Parse a CLZ date string into a date object."""
    if not date_str:
        return None

    date_str = date_str.strip()
    if not date_str:
        return None

    for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _parse_price(price_str: str | None) -> float | None:
    """Parse a price string from CLZ CSV."""
    if not price_str:
        return None
    try:
        cleaned = str(price_str).strip().replace("$", "").strip()
        if cleaned:
            return float(cleaned)
    except ValueError:
        pass
    return None


def _parse_page_count(page_str: str | None) -> int | None:
    """Parse a page count string."""
    if not page_str:
        return None
    try:
        cleaned = str(page_str).strip().split()[0]
        if cleaned.isdigit():
            return int(cleaned)
    except (ValueError, IndexError):
        pass
    return None


def _clean_upc(upc_str: str | None) -> str | None:
    """Clean a UPC/barcode string."""
    if not upc_str:
        return None
    cleaned = str(upc_str).strip().replace(" ", "").replace("-", "")
    if cleaned and cleaned.isdigit():
        return cleaned
    return None
