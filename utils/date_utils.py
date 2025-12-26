from __future__ import annotations

from datetime import date
from dateutil.parser import parse


def to_date(d: str) -> date:
    """Parse a date string into a date object. Accepts ISO (YYYY-MM-DD) and many common formats."""
    return parse(d).date()


def in_range(d: date, start: date, end: date) -> bool:
    """Inclusive date range check."""
    return start <= d <= end
