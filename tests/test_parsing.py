"""Tests for longbox_commons.parsing — issue number parser."""

from longbox_commons.parsing import (
    ParseResult,
    normalize_unicode_symbols,
    parse_format_issue,
    parse_issue_candidate,
)


class TestValidIssueNumbers:
    """Valid issue number formats."""

    def test_decimal_issue(self) -> None:
        result = parse_issue_candidate("0.5")
        assert result.success is True
        assert result.canonical_issue_number == "0.5"
        assert result.variant_suffix is None

    def test_fractional_issue(self) -> None:
        result = parse_issue_candidate("1/2")
        assert result.success is True
        assert result.canonical_issue_number == "1/2"

    def test_negative_issue_with_hash(self) -> None:
        result = parse_issue_candidate("#-1")
        assert result.success is True
        assert result.canonical_issue_number == "-1"

    def test_negative_with_variant(self) -> None:
        result = parse_issue_candidate("-1A")
        assert result.success is True
        assert result.canonical_issue_number == "-1"
        assert result.variant_suffix == "A"

    def test_high_number_with_distribution_code(self) -> None:
        result = parse_issue_candidate("1000.DE")
        assert result.success is True
        assert result.canonical_issue_number == "1000"
        assert result.variant_suffix == "DE"

    def test_letter_variant(self) -> None:
        result = parse_issue_candidate("12B")
        assert result.success is True
        assert result.canonical_issue_number == "12"
        assert result.variant_suffix == "B"

    def test_zero_issue(self) -> None:
        result = parse_issue_candidate("0")
        assert result.success is True
        assert result.canonical_issue_number == "0"

    def test_complex_variant_with_dots(self) -> None:
        result = parse_issue_candidate("-1.WIZ.SIGNED")
        assert result.success is True
        assert result.canonical_issue_number == "-1"
        assert result.variant_suffix == "WIZ.SIGNED"

    def test_whitespace_handling(self) -> None:
        result = parse_issue_candidate("  #-1  ")
        assert result.success is True
        assert result.raw == "  #-1  "
        assert result.canonical_issue_number == "-1"

    def test_plain_number(self) -> None:
        result = parse_issue_candidate("1")
        assert result.success is True
        assert result.canonical_issue_number == "1"

    def test_leading_zeros_preserved(self) -> None:
        result = parse_issue_candidate("0001")
        assert result.success is True
        assert result.canonical_issue_number == "0001"

    def test_variant_with_decimal_issue(self) -> None:
        result = parse_issue_candidate("1.5A")
        assert result.success is True
        assert result.canonical_issue_number == "1.5"
        assert result.variant_suffix == "A"

    def test_negative_decimal_with_variant(self) -> None:
        result = parse_issue_candidate("-0.5B")
        assert result.success is True
        assert result.canonical_issue_number == "-0.5"
        assert result.variant_suffix == "B"

    def test_inf_issue(self) -> None:
        result = parse_issue_candidate("INF")
        assert result.success is True
        assert result.canonical_issue_number == "INF"


class TestInvalidIssueNumbers:
    """Invalid issue number formats."""

    def test_empty_string(self) -> None:
        result = parse_issue_candidate("")
        assert result.success is False
        assert result.error_code == "EMPTY_INPUT"

    def test_whitespace_only(self) -> None:
        result = parse_issue_candidate("   ")
        assert result.success is False
        assert result.error_code == "EMPTY_INPUT"

    def test_none_input(self) -> None:
        result: ParseResult = parse_issue_candidate(None)  # type: ignore[arg-type]
        assert result.success is False
        assert result.error_code == "EMPTY_INPUT"

    def test_only_separator_hyphen(self) -> None:
        result = parse_issue_candidate("-")
        assert result.success is False
        assert result.error_code == "ONLY_SEPARATOR"

    def test_only_separator_dot(self) -> None:
        result = parse_issue_candidate(".")
        assert result.success is False
        assert result.error_code == "ONLY_SEPARATOR"

    def test_only_separator_slash(self) -> None:
        result = parse_issue_candidate("/")
        assert result.success is False
        assert result.error_code == "ONLY_SEPARATOR"

    def test_only_letters(self) -> None:
        result = parse_issue_candidate("ABC")
        assert result.success is False
        assert result.error_code == "INVALID_FORMAT"

    def test_multiple_dots(self) -> None:
        result = parse_issue_candidate("1..2")
        assert result.success is False
        assert result.error_code == "INVALID_FORMAT"

    def test_multiple_slashes(self) -> None:
        result = parse_issue_candidate("1//2")
        assert result.success is False
        assert result.error_code == "INVALID_FORMAT"

    def test_hash_only(self) -> None:
        result = parse_issue_candidate("#")
        assert result.success is False
        assert result.error_code == "ONLY_SEPARATOR"

    def test_invalid_variant_chars(self) -> None:
        result = parse_issue_candidate("1A!")
        assert result.success is False
        assert result.error_code == "INVALID_FORMAT"


class TestMultiIssueRanges:
    """Multi-issue range detection."""

    def test_hyphen_range(self) -> None:
        result = parse_issue_candidate("1-3")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_ampersand_range(self) -> None:
        result = parse_issue_candidate("5 & 6")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_comma_range(self) -> None:
        result = parse_issue_candidate("7,8")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_triple_hyphen_range(self) -> None:
        result = parse_issue_candidate("1-2-3")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_letter_range(self) -> None:
        result = parse_issue_candidate("1A-1C")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_same_number_range(self) -> None:
        result = parse_issue_candidate("1-1")
        assert result.success is False
        assert result.error_code == "MULTI_ISSUE_RANGE"

    def test_series_prefix_invalid(self) -> None:
        result = parse_issue_candidate("X-Men -1")
        assert result.success is False
        assert result.error_code == "INVALID_FORMAT"


class TestUnicodeNormalization:
    """Unicode symbol normalization."""

    def test_half_fraction(self) -> None:
        assert normalize_unicode_symbols("½") == "1/2"

    def test_half_with_variant(self) -> None:
        assert normalize_unicode_symbols("½-A") == "1/2A"

    def test_infinity(self) -> None:
        assert normalize_unicode_symbols("∞") == "INF"

    def test_infinity_with_variant(self) -> None:
        assert normalize_unicode_symbols("∞-A") == "INFA"

    def test_quarter(self) -> None:
        assert normalize_unicode_symbols("¼") == "1/4"

    def test_no_unicode(self) -> None:
        assert normalize_unicode_symbols("12B") == "12B"


class TestFormatIssueParsing:
    """CLZ format-as-issue-number patterns."""

    def test_bare_tp(self) -> None:
        assert parse_format_issue("TP") == ("1", "TP")

    def test_bare_hc(self) -> None:
        assert parse_format_issue("HC") == ("1", "HC")

    def test_tp_with_volume(self) -> None:
        assert parse_format_issue("TP-2") == ("2", "TP")

    def test_tp_with_letter(self) -> None:
        assert parse_format_issue("TP-D") == ("1", "TP-D")

    def test_number_format_code(self) -> None:
        assert parse_format_issue("1HC") == ("1", "HC")

    def test_number_format_with_variant(self) -> None:
        assert parse_format_issue("1HC-E") == ("1", "HC-E")

    def test_not_a_format(self) -> None:
        assert parse_format_issue("12B") is None

    def test_bare_gn(self) -> None:
        assert parse_format_issue("GN") == ("1", "GN")
