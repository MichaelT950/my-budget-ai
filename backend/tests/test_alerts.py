"""Tests for AlertService — due date, overdraft, and expense threshold alerts."""

from datetime import date, timedelta

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.statement_repo import StatementRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.statement import StatementSnapshot
from src.models.transaction import Transaction
from src.services.alerts import AlertService
from src.services.balance_calculator import BalanceCalculator
from src.services.cash_flow import CashFlowService


class TestAlertService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        stmt_repo = StatementRepository(conn)
        txn_repo = TransactionRepository(conn)
        cat_repo = CategoryRepository(conn)
        calc = BalanceCalculator(acct_repo, txn_repo)
        cf_svc = CashFlowService(txn_repo, cat_repo)
        svc = AlertService(stmt_repo, acct_repo, calc, cf_svc)
        return acct_repo, stmt_repo, txn_repo, svc

    # --- Due date alerts ---

    def test_due_within_7_days_triggers_alert(self, conn):
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="Chase CC", type="credit_card"))

        due = date.today() + timedelta(days=3)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(),
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 1
        assert "Chase CC" in alerts[0].message
        assert "3 days" in alerts[0].message

    def test_paid_snapshots_excluded(self, conn):
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        due = date.today() + timedelta(days=3)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(), is_paid=True,
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 0

    def test_outside_window_excluded(self, conn):
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        # Due in 10 days — outside 7-day window
        due = date.today() + timedelta(days=10)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(),
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 0

    def test_past_due_excluded(self, conn):
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        # Due yesterday — already past
        due = date.today() - timedelta(days=1)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(),
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 0

    def test_empty_state(self, conn):
        _, _, _, svc = self._setup(conn)
        alerts = svc.get_all_alerts()
        assert alerts == []

    def test_due_today(self, conn):
        acct_repo, stmt_repo, _, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=250.0, due_date=date.today().isoformat(),
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 1
        assert "0 days" in alerts[0].message

    # --- Overdraft alerts ---

    def test_overdraft_triggers_alert(self, conn):
        """A checking account with negative balance should produce an error alert."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(
            name="Main Checking", type="checking", starting_balance=100.0,
        ))
        # Spend more than the starting balance
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=200.0,
            description="Big purchase", date=date.today().isoformat(),
        ))
        alerts = svc.get_overdraft_alerts()
        assert len(alerts) == 1
        assert "Main Checking" in alerts[0].message
        assert "overdraft" in alerts[0].message
        assert alerts[0].alert_type == "error"

    def test_no_overdraft_positive_balance(self, conn):
        """Positive balance should not trigger an overdraft alert."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        acct_repo.create(Account(
            name="Savings", type="savings", starting_balance=5000.0,
        ))
        alerts = svc.get_overdraft_alerts()
        assert len(alerts) == 0

    def test_credit_cards_excluded_from_overdraft(self, conn):
        """Credit cards always have 'debt' so they should not trigger overdraft."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        cc = acct_repo.create(Account(
            name="CC", type="credit_card", starting_balance=0.0,
        ))
        txn_repo.create(Transaction(
            account_id=cc.id, type="expense", amount=500.0,
            description="Purchase", date=date.today().isoformat(),
        ))
        alerts = svc.get_overdraft_alerts()
        assert len(alerts) == 0

    # --- Expense threshold alerts ---

    def test_expense_threshold_triggers_at_90_percent(self, conn):
        """Expenses >= 90% of income should trigger a warning."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=10000.0,
        ))
        today = date.today().isoformat()
        txn_repo.create(Transaction(
            account_id=checking.id, type="income", amount=5000.0,
            description="Salary", date=today,
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=4600.0,
            description="Rent", date=today,
        ))
        alerts = svc.get_expense_threshold_alerts()
        assert len(alerts) == 1
        assert "92%" in alerts[0].message
        assert alerts[0].alert_type == "warning"

    def test_expense_exceeding_income_is_error(self, conn):
        """Expenses > 100% of income should produce an error alert."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=10000.0,
        ))
        today = date.today().isoformat()
        txn_repo.create(Transaction(
            account_id=checking.id, type="income", amount=3000.0,
            description="Salary", date=today,
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=3500.0,
            description="Expenses", date=today,
        ))
        alerts = svc.get_expense_threshold_alerts()
        assert len(alerts) == 1
        assert alerts[0].alert_type == "error"

    def test_no_threshold_alert_below_90_percent(self, conn):
        """Expenses below 90% should not trigger an alert."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=10000.0,
        ))
        today = date.today().isoformat()
        txn_repo.create(Transaction(
            account_id=checking.id, type="income", amount=5000.0,
            description="Salary", date=today,
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=2000.0,
            description="Groceries", date=today,
        ))
        alerts = svc.get_expense_threshold_alerts()
        assert len(alerts) == 0

    def test_no_threshold_alert_with_zero_income(self, conn):
        """Zero income should not trigger an expense threshold alert."""
        acct_repo, _, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=10000.0,
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=500.0,
            description="Groceries", date=date.today().isoformat(),
        ))
        alerts = svc.get_expense_threshold_alerts()
        assert len(alerts) == 0

    # --- get_all_alerts combines all types ---

    def test_get_all_alerts_combines_all_types(self, conn):
        """get_all_alerts should return alerts from all three sources."""
        acct_repo, stmt_repo, txn_repo, svc = self._setup(conn)

        # Overdraft: checking with negative balance
        checking = acct_repo.create(Account(
            name="Checking", type="checking", starting_balance=100.0,
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="expense", amount=200.0,
            description="Overspend", date=date.today().isoformat(),
        ))

        # Due date: CC with statement due in 3 days
        cc = acct_repo.create(Account(name="CC", type="credit_card"))
        due = date.today() + timedelta(days=3)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(),
        ))

        alerts = svc.get_all_alerts()
        alert_types = {a.alert_type for a in alerts}
        # Should have at least due date warning and overdraft error
        assert "warning" in alert_types
        assert "error" in alert_types
        assert len(alerts) >= 2
