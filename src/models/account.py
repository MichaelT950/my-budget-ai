"""Account model — credit cards, checking, and savings accounts."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Account:
    id: int | None = None
    name: str = ""
    type: str = ""  # credit_card, checking, savings
    starting_balance: float = 0.0
    credit_limit: float | None = None
    statement_close_day: int | None = None
    payment_due_day: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
