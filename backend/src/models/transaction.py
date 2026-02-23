"""Transaction model — income, expense, and transfer transactions."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Transaction:
    id: int | None = None
    account_id: int = 0
    type: str = ""  # income, expense, transfer
    amount: float = 0.0  # always positive
    description: str = ""
    category_id: int | None = None
    date: str = ""  # YYYY-MM-DD
    transfer_to_account_id: int | None = None
    notes: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
