"""Statement auto-calculation — create snapshots on startup for CC accounts."""

from datetime import date

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository
from src.models.statement import StatementSnapshot
from src.services.balance_calculator import BalanceCalculator


class StatementService:
    def __init__(
        self,
        account_repo: AccountRepository,
        statement_repo: StatementRepository,
        balance_calculator: BalanceCalculator,
    ):
        self.account_repo = account_repo
        self.statement_repo = statement_repo
        self.balance_calculator = balance_calculator

    def auto_create_statements(self):
        """Check CC accounts and create statement snapshots if today >= statement_close_day
        and no snapshot exists for the current month."""
        today = date.today()
        accounts = self.account_repo.get_all()

        for acct in accounts:
            if acct.type != "credit_card" or not acct.statement_close_day:
                continue

            if today.day < acct.statement_close_day:
                continue

            # Check if snapshot already exists for this month
            statement_date = today.replace(day=acct.statement_close_day)
            existing = self.statement_repo.get_by_account(acct.id)
            already_exists = any(s.statement_date == statement_date.isoformat() for s in existing)
            if already_exists:
                continue

            balance = self.balance_calculator.get_balance(acct)

            # Calculate due date
            if acct.payment_due_day:
                if acct.payment_due_day > acct.statement_close_day:
                    due_date = today.replace(day=acct.payment_due_day)
                else:
                    # Due day is in next month
                    if today.month == 12:
                        due_date = today.replace(year=today.year + 1, month=1, day=acct.payment_due_day)
                    else:
                        due_date = today.replace(month=today.month + 1, day=acct.payment_due_day)
            else:
                due_date = statement_date

            self.statement_repo.create(StatementSnapshot(
                account_id=acct.id,
                statement_date=statement_date.isoformat(),
                balance=balance,
                due_date=due_date.isoformat(),
            ))
