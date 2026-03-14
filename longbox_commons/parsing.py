"""Issue number parsing and normalization.

Parses raw issue number strings into canonical form with optional variant suffix.
Handles negative issues, decimals, fractions, format codes, unicode symbols,
and multi-issue range detection.
"""

import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    """Result of parsing a raw issue number string."""

    success: bool
    raw: str
    canonical_issue_number: str | None = None
    variant_suffix: str | None = None
    error_code: str | None = None
    error_message: str | None = None


FORMAT_ISSUE_CODES = frozenset(
    {
        "TP",
        "HC",
        "GN",
        "SC",
        "TPB",
        "OGN",
        "OM",
    }
)

UNICODE_SYMBOLS: dict[str, str] = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅕": "1/5",
    "⅙": "1/6",
    "⅛": "1/8",
    "∞": "INF",
}


def normalize_unicode_symbols(raw: str) -> str:
    """Replace unicode fraction/symbol characters with ASCII equivalents.

    Handles CLZ-style separators like ``½-A`` → ``1/2A`` and ``∞-A`` → ``INFA``.
    """
    for char, replacement in UNICODE_SYMBOLS.items():
        if char in raw:
            raw = raw.replace(char, replacement)
            if "/" in replacement:
                raw = re.sub(r"(\d/\d+)-([A-Za-z])", r"\1\2", raw)
            if replacement == "INF":
                raw = re.sub(r"^INF-([A-Za-z])", r"INF\1", raw)
    return raw


def parse_format_issue(raw: str) -> tuple[str, str] | None:
    """Parse CLZ format-as-issue-number patterns.

    Examples::

        "TP"   → ("1", "TP")
        "HC-2" → ("2", "HC")
        "1HC-E" → ("1", "HC-E")

    Returns:
        ``(canonical_issue_number, variant_suffix)`` or ``None``.
    """
    upper = raw.upper()

    if upper in FORMAT_ISSUE_CODES:
        return ("1", upper)

    fmt_suffix = re.match(r"^([A-Z]+)-([A-Z0-9]+)$", upper)
    if fmt_suffix and fmt_suffix.group(1) in FORMAT_ISSUE_CODES:
        suffix = fmt_suffix.group(2)
        if suffix.isdigit():
            return (suffix, fmt_suffix.group(1))
        return ("1", f"{fmt_suffix.group(1)}-{suffix}")

    num_fmt = re.match(r"^(\d+)([A-Z]+)(?:-([A-Za-z]+))?$", upper)
    if num_fmt and num_fmt.group(2) in FORMAT_ISSUE_CODES:
        variant = num_fmt.group(2)
        if num_fmt.group(3):
            variant = f"{variant}-{num_fmt.group(3)}"
        return (num_fmt.group(1), variant)

    return None


def parse_issue_candidate(raw: str) -> ParseResult:
    """Parse a comic issue number candidate string.

    Args:
        raw: Raw input string (e.g., ``"#-1"``, ``"0.5"``, ``"12B"``, ``"1-3"``).

    Returns:
        ParseResult with canonical issue number and optional variant suffix,
        or error details on failure.
    """
    if raw is None:
        return ParseResult(
            success=False,
            raw="",
            error_code="EMPTY_INPUT",
            error_message="Issue number cannot be empty",
        )

    preserved_raw = raw
    working = raw.strip()

    if not working:
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="EMPTY_INPUT",
            error_message="Issue number cannot be empty",
        )

    if re.match(r"^\d+\s*-\s*\d+$", working):
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="MULTI_ISSUE_RANGE",
            error_message="Multiple issues detected, use single issue parsing",
        )

    if re.search(r"\d+-\d+-\d+", working):
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="MULTI_ISSUE_RANGE",
            error_message="Multiple issues detected, use single issue parsing",
        )

    if re.search(r"\d+\s*&\s*\d+", working):
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="MULTI_ISSUE_RANGE",
            error_message="Multiple issues detected, use single issue parsing",
        )

    if re.search(r"\d+\s*,\s*\d+", working):
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="MULTI_ISSUE_RANGE",
            error_message="Multiple issues detected, use single issue parsing",
        )

    if re.match(r"^\d+[A-Za-z]\s*-\s*\d+[A-Za-z]$", working):
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="MULTI_ISSUE_RANGE",
            error_message="Multiple issues detected, use single issue parsing",
        )

    if working.startswith("#"):
        working = working[1:].lstrip()

    if not working:
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="ONLY_SEPARATOR",
            error_message="Issue number must contain digits",
        )

    if working in ["-", ".", "/"]:
        return ParseResult(
            success=False,
            raw=preserved_raw,
            error_code="ONLY_SEPARATOR",
            error_message="Issue number must contain digits",
        )

    special_token_match = re.match(r"^(INF)(?=[A-Za-z.]|$)", working, re.IGNORECASE)
    if special_token_match:
        canonical_issue_number = special_token_match.group(1).upper()
        working_after = working[len(canonical_issue_number):]
    else:
        canonical_pattern = r"^(-?\d+(\.\d+)?(/\d+)?)"
        match = re.match(canonical_pattern, working)

        if not match:
            return ParseResult(
                success=False,
                raw=preserved_raw,
                error_code="INVALID_FORMAT",
                error_message="Invalid issue number format",
            )

        canonical_issue_number = match.group(0)
        working_after = working[len(canonical_issue_number):]

    variant_suffix = None
    remaining = working_after
    if remaining:
        if re.match(r"^(\.?)[A-Za-z]", remaining):
            if re.match(r"^[A-Za-z.]+$", remaining):
                variant_suffix = remaining[1:] if remaining.startswith(".") else remaining
            else:
                return ParseResult(
                    success=False,
                    raw=preserved_raw,
                    error_code="INVALID_FORMAT",
                    error_message="Invalid issue number format",
                )
        else:
            return ParseResult(
                success=False,
                raw=preserved_raw,
                error_code="INVALID_FORMAT",
                error_message="Invalid issue number format",
            )

    return ParseResult(
        success=True,
        raw=preserved_raw,
        canonical_issue_number=canonical_issue_number,
        variant_suffix=variant_suffix,
    )
