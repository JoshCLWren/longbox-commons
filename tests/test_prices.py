"""Tests for longbox_commons.prices."""

from longbox_commons.prices import parse_price


class TestParsePrice:
    """Price parsing from raw strings."""

    def test_simple_dollar(self) -> None:
        assert parse_price("$12.99") == 12.99

    def test_no_symbol(self) -> None:
        assert parse_price("3.50") == 3.50

    def test_with_currency_suffix(self) -> None:
        assert parse_price("1.95 USD") == 1.95

    def test_with_commas(self) -> None:
        assert parse_price("$1,299.00") == 1299.00

    def test_empty_string(self) -> None:
        assert parse_price("") == 0.0

    def test_none(self) -> None:
        assert parse_price(None) == 0.0

    def test_no_digits(self) -> None:
        assert parse_price("free") == 0.0

    def test_multiple_decimals(self) -> None:
        assert parse_price("1.2.3") == 1.2

    def test_zero(self) -> None:
        assert parse_price("$0.00") == 0.0

    def test_large_price(self) -> None:
        assert parse_price("$999.99") == 999.99

    def test_only_dot(self) -> None:
        assert parse_price(".") == 0.0
