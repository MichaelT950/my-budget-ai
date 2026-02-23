"""Tests for StatementService — auto-creating statement snapshots for CC accounts.

StatementService runs on startup to auto-create monthly statement snapshots when
today >= statement_close_day. This matters because it triggers due-date alerts
and drives the billing cycle management in the dashboard.
"""

from datetime import date
from unittest.mock import patch

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.transaction import Transaction
from src.services.balance_calculator import BalanceCalculator
from src.services.statement_service import StatementService


class TestStatementService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        stmt_repo = StatementRepository(conn)
        txn_repo = TransactionRepository(conn)
        calc = BalanceCalculator(acct_repo, txn_repo)
        svc = StatementService(acct_repo, stmt_repo, calc)
        return acct_repo, stmt_repo, txn_repo, svc

    def test_creates_snapshot_on_close_day(self, conn):
        """Snapshot should be created when today >= statement_close_day."""
        acct_repo, stmt_repo, txn_repo, svc = self._setup(conn)
        cc = acct_repo.create(Account(
            name="Chase CC", type="credit_card",
            starting_balance=0.0, statement_close_day=15, payment_due_day=25,
        ))
        txn_repo.create(Transaction(
            account_id=cc.id, type="expense", amount=200.0,
            description="Purchase", date="2025-01-10",
        ))

        # Simulate today is the 15th (close day)
        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 15)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        stmts = stmt_repo.get_by_account(cc.id)
        assert len(stmts) == 1
        assert stmts[0].statement_date == "2025-01-15"
        assert stmts[0].balance == 200.0  # starting 0 + 200 expenses
        assert stmts[0].due_date == "2025-01-25"  # due_day > close_day → same month

    def test_skips_non_credit_card_accounts(self, conn):
        """Checking and savings accounts should not get statement snapshots."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=5000.0,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 20)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        # No snapshots should exist for checking accounts
        assert stmt_repo.get_unpaid() == []

    def test_skips_when_before_close_day(self, conn):
        """No snapshot if today < statement_close_day."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="CC", type="credit_card",
            starting_balance=0.0, statement_close_day=20, payment_due_day=28,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 10)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        assert stmt_repo.get_unpaid() == []

    def test_idempotent_does_not_duplicate(self, conn):
        """Running auto_create_statements twice should not create duplicate snapshots."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="CC", type="credit_card",
            starting_balance=0.0, statement_close_day=15, payment_due_day=25,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 15)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()
            svc.auto_create_statements()

        unpaid = stmt_repo.get_unpaid()
        assert len(unpaid) == 1

    def test_due_date_next_month_when_due_day_less_than_close_day(self, conn):
        """When payment_due_day < statement_close_day, due date rolls to next month."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="CC", type="credit_card",
            starting_balance=0.0, statement_close_day=25, payment_due_day=10,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 25)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        stmts = stmt_repo.get_unpaid()
        assert len(stmts) == 1
        assert stmts[0].due_date == "2025-02-10"

    def test_december_close_rolls_due_to_january(self, conn):
        """December close with due_day < close_day should roll to January next year."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="CC", type="credit_card",
            starting_balance=0.0, statement_close_day=20, payment_due_day=5,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 12, 20)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        stmts = stmt_repo.get_unpaid()
        assert len(stmts) == 1
        assert stmts[0].due_date == "2026-01-05"

    def test_skips_account_without_close_day(self, conn):
        """CC accounts without statement_close_day should be skipped."""
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        acct_repo.create(Account(
            name="CC", type="credit_card",
            starting_balance=0.0, statement_close_day=None,
        ))

        with patch("src.services.statement_service.date") as mock_date:
            mock_date.today.return_value = date(2025, 1, 15)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.auto_create_statements()

        assert stmt_repo.get_unpaid() == []
