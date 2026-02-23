"""Date parsing and validation utilities."""

from datetime import date, datetime


def parse_date(date_str: str) -> date:
    """Parse a date string supporting YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY, M/D/YYYY.

    Handles both zero-padded (01/05/2024) and unpadded (1/5/2024) dates by
    stripping leading zeros from month/day components before parsing.
    """
    stripped = date_str.strip()

    # Try ISO format first (always zero-padded)
    try:
        return datetime.strptime(stripped, "%Y-%m-%d").date()
    except ValueError:
        pass

    # For M/D/Y and M-D-Y formats, normalize by stripping leading zeros
    # so a single set of formats handles both padded and unpadded input.
    for sep in ("/", "-"):
        parts = stripped.split(sep)
        if len(parts) == 3:
            try:
                month = int(parts[0])
                day = int(parts[1])
                year = int(parts[2])
                return date(year, month, day)
            except (ValueError, OverflowError):
                continue

    raise ValueError(f"Unable to parse date: {date_str!r}")


def is_future_date(d: date) -> bool:
    """Return True if the given date is in the future."""
    return d > date.today()
