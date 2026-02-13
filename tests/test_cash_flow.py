"""Tests for CashFlowService — totals, transfers excluded, category breakdown, filtering."""

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.transaction import Transaction
from src.services.cash_flow import CashFlowService


class TestCashFlowService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        txn_repo = TransactionRepository(conn)
        cat_repo = CategoryRepository(conn)
        svc = CashFlowService(txn_repo, cat_repo)
        return acct_repo, txn_repo, cat_repo, svc

    def test_correct_totals(self, conn):
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
        result = svc.get_cash_flow("2024-01-01", "2024-01-31")
        assert result.total_income == 5000.0
        assert result.total_expenses == 200.0
        assert result.net_cash_flow == 4800.0

    def test_transfers_excluded(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(name="Checking", type="checking"))
        savings = acct_repo.create(Account(name="Savings", type="savings"))

        txn_repo.create(Transaction(
            account_id=checking.id, type="transfer", amount=500.0,
            description="To savings", date="2024-01-15",
            transfer_to_account_id=savings.id,
        ))
        result = svc.get_cash_flow("2024-01-01", "2024-01-31")
        assert result.total_income == 0.0
        assert result.total_expenses == 0.0
        assert result.net_cash_flow == 0.0

    def test_category_breakdown(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))
        food_cat = cat_repo.get_by_name("Food & Drink")
        transport_cat = cat_repo.get_by_name("Transportation")

        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=100.0,
            description="Restaurant", category_id=food_cat.id, date="2024-01-10",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=50.0,
            description="Gas", category_id=transport_cat.id, date="2024-01-12",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=75.0,
            description="Grocery", category_id=food_cat.id, date="2024-01-15",
        ))
        result = svc.get_cash_flow("2024-01-01", "2024-01-31")
        assert result.expenses_by_category["Food & Drink"] == 175.0
        assert result.expenses_by_category["Transportation"] == 50.0

    def test_date_filtering(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking"))

        txn_repo.create(Transaction(
            account_id=acct.id, type="income", amount=1000.0,
            description="Jan income", date="2024-01-15",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="income", amount=2000.0,
            description="Feb income", date="2024-02-15",
        ))
        result = svc.get_cash_flow("2024-01-01", "2024-01-31")
        assert result.total_income == 1000.0

    def test_single_account_filtering(self, conn):
        acct_repo, txn_repo, cat_repo, svc = self._setup(conn)
        acct1 = acct_repo.create(Account(name="Checking", type="checking"))
        acct2 = acct_repo.create(Account(name="Savings", type="savings"))

        txn_repo.create(Transaction(
            account_id=acct1.id, type="income", amount=1000.0,
            description="Income 1", date="2024-01-15",
        ))
        txn_repo.create(Transaction(
            account_id=acct2.id, type="income", amount=500.0,
            description="Income 2", date="2024-01-15",
        ))
        result = svc.get_cash_flow("2024-01-01", "2024-01-31", account_id=acct1.id)
        assert result.total_income == 1000.0
