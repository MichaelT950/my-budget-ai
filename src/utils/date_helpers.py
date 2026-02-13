"""Date parsing and validation utilities."""

from datetime import date, datetime


def parse_date(date_str: str) -> date:
    """Parse a date string supporting YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY, M/D/YYYY."""
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str!r}")


def is_future_date(d: date) -> bool:
    """Return True if the given date is in the future."""
    return d > date.today()
