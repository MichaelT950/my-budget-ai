"""Tests for src/utils/date_helpers.py."""

from datetime import date, timedelta

import pytest

from src.utils.date_helpers import is_future_date, parse_date


class TestParseDate:
    def test_iso_format(self):
        assert parse_date("2024-01-05") == date(2024, 1, 5)

    def test_slash_padded(self):
        assert parse_date("01/05/2024") == date(2024, 1, 5)

    def test_slash_unpadded(self):
        assert parse_date("1/5/2024") == date(2024, 1, 5)

    def test_dash_separator(self):
        assert parse_date("01-05-2024") == date(2024, 1, 5)

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_date("not-a-date")


class TestIsFutureDate:
    def test_tomorrow_is_future(self):
        tomorrow = date.today() + timedelta(days=1)
        assert is_future_date(tomorrow) is True

    def test_today_is_not_future(self):
        assert is_future_date(date.today()) is False

    def test_yesterday_is_not_future(self):
        yesterday = date.today() - timedelta(days=1)
        assert is_future_date(yesterday) is False
