"""Tests for BalanceSheetService — net worth, partitioning, empty state."""

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.transaction import Transaction
from src.services.balance_calculator import BalanceCalculator
from src.services.balance_sheet import BalanceSheetService


class TestBalanceSheetService:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        txn_repo = TransactionRepository(conn)
        calc = BalanceCalculator(acct_repo, txn_repo)
        svc = BalanceSheetService(acct_repo, calc)
        return acct_repo, txn_repo, svc

    def test_net_worth_assets_minus_liabilities(self, conn):
        acct_repo, txn_repo, svc = self._setup(conn)
        acct_repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))
        acct_repo.create(Account(name="CC", type="credit_card", starting_balance=1000.0))

        result = svc.get_balance_sheet()
        assert result.total_assets == 5000.0
        assert result.total_liabilities == 1000.0
        assert result.net_worth == 4000.0

    def test_correct_partitioning(self, conn):
        acct_repo, txn_repo, svc = self._setup(conn)
        acct_repo.create(Account(name="Checking", type="checking", starting_balance=3000.0))
        acct_repo.create(Account(name="Savings", type="savings", starting_balance=10000.0))
        acct_repo.create(Account(name="CC 1", type="credit_card", starting_balance=500.0))
        acct_repo.create(Account(name="CC 2", type="credit_card", starting_balance=200.0))

        result = svc.get_balance_sheet()
        assert "Checking" in result.assets
        assert "Savings" in result.assets
        assert "CC 1" in result.liabilities
        assert "CC 2" in result.liabilities
        assert result.total_assets == 13000.0
        assert result.total_liabilities == 700.0

    def test_empty_state(self, conn):
        _, _, svc = self._setup(conn)
        result = svc.get_balance_sheet()
        assert result.total_assets == 0.0
        assert result.total_liabilities == 0.0
        assert result.net_worth == 0.0
        assert result.assets == {}
        assert result.liabilities == {}

    def test_with_transactions(self, conn):
        acct_repo, txn_repo, svc = self._setup(conn)
        checking = acct_repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))
        cc = acct_repo.create(Account(name="CC", type="credit_card", starting_balance=0.0))

        txn_repo.create(Transaction(
            account_id=cc.id, type="expense", amount=300.0,
            description="Purchase", date="2024-01-10",
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="transfer", amount=100.0,
            description="CC Payment", date="2024-01-20",
            transfer_to_account_id=cc.id,
        ))

        result = svc.get_balance_sheet()
        # Checking: 5000 - 100 = 4900
        assert result.assets["Checking"] == 4900.0
        # CC: 0 + 300 - 100 = 200
        assert result.liabilities["CC"] == 200.0
        assert result.net_worth == 4700.0
