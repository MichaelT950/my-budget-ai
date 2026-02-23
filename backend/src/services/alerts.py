"""Alert service — payment due date warnings."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository


@dataclass
class Alert:
    message: str
    alert_type: str = "warning"  # warning, info, error
    account_name: str = ""
    due_date: str = ""
    balance: float = 0.0


class AlertService:
    def __init__(self, statement_repo: StatementRepository, account_repo: AccountRepository):
        self.statement_repo = statement_repo
        self.account_repo = account_repo

    def get_due_date_alerts(self) -> list[Alert]:
        """Get alerts for unpaid statements due within 7 days."""
        unpaid = self.statement_repo.get_unpaid()
        accounts = {a.id: a for a in self.account_repo.get_all()}
        today = date.today()
        window_end = today + timedelta(days=7)
        alerts = []

        for stmt in unpaid:
            try:
                due = date.fromisoformat(stmt.due_date)
            except ValueError:
                continue

            if today <= due <= window_end:
                acct = accounts.get(stmt.account_id)
                acct_name = acct.name if acct else "Unknown"
                days_left = (due - today).days
                day_word = "day" if days_left == 1 else "days"

                alerts.append(Alert(
                    message=f"{acct_name}: ${stmt.balance:,.2f} due in {days_left} {day_word} ({stmt.due_date})",
                    alert_type="warning",
                    account_name=acct_name,
                    due_date=stmt.due_date,
                    balance=stmt.balance,
                ))

        return alerts

    def get_all_alerts(self) -> list[Alert]:
        """Get all alerts (currently just due date alerts)."""
        return self.get_due_date_alerts()
