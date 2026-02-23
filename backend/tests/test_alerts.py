"""Tests for AlertService — due date alerts, paid excluded, window, empty state."""

from datetime import date, timedelta

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository
from src.models.account import Account
from src.models.statement import StatementSnapshot
from src.services.alerts import AlertService


class TestAlertService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        stmt_repo = StatementRepository(conn)
        svc = AlertService(stmt_repo, acct_repo)
        return acct_repo, stmt_repo, svc

    def test_due_within_7_days_triggers_alert(self, conn):
        acct_repo, stmt_repo, svc = self._setup(conn)
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
        acct_repo, stmt_repo, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        due = date.today() + timedelta(days=3)
        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=500.0, due_date=due.isoformat(), is_paid=True,
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 0

    def test_outside_window_excluded(self, conn):
        acct_repo, stmt_repo, svc = self._setup(conn)
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
        acct_repo, stmt_repo, svc = self._setup(conn)
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
        _, _, svc = self._setup(conn)
        alerts = svc.get_all_alerts()
        assert alerts == []

    def test_due_today(self, conn):
        acct_repo, stmt_repo, svc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card"))

        stmt_repo.create(StatementSnapshot(
            account_id=cc.id, statement_date="2024-01-15",
            balance=250.0, due_date=date.today().isoformat(),
        ))
        alerts = svc.get_due_date_alerts()
        assert len(alerts) == 1
        assert "0 days" in alerts[0].message
