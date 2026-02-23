"""Tests for ReportService — monthly/weekly summaries, top category, drill-down."""

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.transaction import Transaction
from src.services.reports import ReportService


class TestReportService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        txn_repo = TransactionRepository(conn)
        cat_repo = CategoryRepository(conn)
        svc = ReportService(txn_repo, cat_repo)
        return acct_repo, txn_repo, cat_repo, svc

    def test_monthly_summary(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))
        food_cat = cat_repo.get_by_name("Food & Drink")

        txn_repo.create(Transaction(
            account_id=acct.id, type="income", amount=5000.0,
            description="Paycheck", date="2024-01-15",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=200.0,
            description="Groceries", category_id=food_cat.id, date="2024-01-20",
        ))
        result = svc.get_monthly_summary(2024, 1)
        assert result.total_income == 5000.0
        assert result.total_expenses == 200.0
        assert result.net == 4800.0
        assert result.period_label == "January 2024"

    def test_weekly_summary(self, conn):
        from datetime import date

        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))

        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=50.0,
            description="Lunch", date="2024-01-15",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=30.0,
            description="Coffee", date="2024-01-17",
        ))
        # Jan 15, 2024 is a Monday
        result = svc.get_weekly_summary(date(2024, 1, 15))
        assert result.total_expenses == 80.0
        assert "Week of" in result.period_label

    def test_top_category_detection(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))
        food_cat = cat_repo.get_by_name("Food & Drink")
        transport_cat = cat_repo.get_by_name("Transportation")

        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=500.0,
            description="Groceries", category_id=food_cat.id, date="2024-01-10",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=100.0,
            description="Gas", category_id=transport_cat.id, date="2024-01-12",
        ))
        result = svc.get_monthly_summary(2024, 1)
        assert result.top_category == "Food & Drink"

    def test_drill_down_data(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))
        food_cat = cat_repo.get_by_name("Food & Drink")

        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=50.0,
            description="Restaurant A", category_id=food_cat.id, date="2024-01-10",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=30.0,
            description="Restaurant B", category_id=food_cat.id, date="2024-01-15",
        ))
        result = svc.get_monthly_summary(2024, 1)
        assert len(result.expenses_by_category) == 1
        food_summary = result.expenses_by_category[0]
        assert food_summary.name == "Food & Drink"
        assert food_summary.total == 80.0
        assert food_summary.count == 2
        assert len(food_summary.transactions) == 2

    def test_empty_period(self, conn):
        _, _, _, svc = self._setup(conn)
        result = svc.get_monthly_summary(2024, 1)
        assert result.total_income == 0.0
        assert result.total_expenses == 0.0
        assert result.top_category == ""
        assert result.expenses_by_category == []
