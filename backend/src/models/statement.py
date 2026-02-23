"""StatementSnapshot model — monthly credit card statement records."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StatementSnapshot:
    id: int | None = None
    account_id: int = 0
    statement_date: str = ""  # YYYY-MM-DD
    balance: float = 0.0
    due_date: str = ""  # YYYY-MM-DD
    is_paid: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
