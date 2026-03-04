"""Tests for src/utils/formatters.py."""

from src.utils.formatters import format_currency, format_signed_currency


class TestFormatCurrency:
    def test_basic_formatting(self):
        assert format_currency(1234.50) == "$1,234.50"

    def test_zero_amount(self):
        assert format_currency(0) == "$0.00"

    def test_negative_amount(self):
        assert format_currency(-99.99) == "$-99.99"


class TestFormatSignedCurrency:
    def test_income_has_plus_prefix(self):
        assert format_signed_currency(500.00, "income") == "+$500.00"

    def test_expense_has_minus_prefix(self):
        assert format_signed_currency(75.25, "expense") == "-$75.25"

    def test_transfer_has_no_prefix(self):
        assert format_signed_currency(200.00, "transfer") == "$200.00"
