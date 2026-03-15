"""Tests for longbox_commons.prices."""

from longbox_commons.prices import parse_price


class TestParsePrice:
    """Price parsing from raw strings."""

    def test_simple_dollar(self) -> None:
        """Test parsing simple dollar amount."""
        assert parse_price("$12.99") == 12.99

    def test_no_symbol(self) -> None:
        """Test parsing price without dollar symbol."""
        assert parse_price("3.50") == 3.50

    def test_with_currency_suffix(self) -> None:
        """Test parsing price with currency suffix."""
        assert parse_price("1.95 USD") == 1.95

    def test_with_commas(self) -> None:
        """Test parsing price with comma separators."""
        assert parse_price("$1,299.00") == 1299.00

    def test_empty_string(self) -> None:
        """Test that empty string returns 0.0."""
        assert parse_price("") == 0.0

    def test_none(self) -> None:
        """Test that None returns 0.0."""
        assert parse_price(None) == 0.0

    def test_no_digits(self) -> None:
        """Test that strings with no digits return 0.0."""
        assert parse_price("free") == 0.0

    def test_multiple_decimals(self) -> None:
        """Test that multiple decimals parse first valid portion."""
        assert parse_price("1.2.3") == 1.2

    def test_zero(self) -> None:
        """Test parsing zero price."""
        assert parse_price("$0.00") == 0.0

    def test_large_price(self) -> None:
        """Test parsing large price value."""
        assert parse_price("$999.99") == 999.99

    def test_only_dot(self) -> None:
        """Test that dot-only input returns 0.0."""
        assert parse_price(".") == 0.0
