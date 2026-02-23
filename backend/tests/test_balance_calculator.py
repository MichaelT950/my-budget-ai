"""Tests for BalanceCalculator — checking, CC, empty, and mixed transaction types."""

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.transaction import Transaction
from src.services.balance_calculator import BalanceCalculator


class TestBalanceCalculator:
    def _setup(self, conn):
        acct_repo = AccountRepository(conn)
        txn_repo = TransactionRepository(conn)
        calc = BalanceCalculator(acct_repo, txn_repo)
        return acct_repo, txn_repo, calc

    def test_checking_balance_income_and_expenses(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking", starting_balance=1000.0))
        txn_repo.create(Transaction(
            account_id=acct.id, type="income", amount=3000.0,
            description="Paycheck", date="2024-01-15",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=500.0,
            description="Rent", date="2024-01-20",
        ))
        # 1000 + 3000 - 500 = 3500
        assert calc.get_balance(acct) == 3500.0

    def test_credit_card_balance(self, conn):
        """CC: starting_balance + expenses - payments_received (transfers IN)."""
        acct_repo, txn_repo, calc = self._setup(conn)
        checking = acct_repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))
        cc = acct_repo.create(Account(
            name="Chase CC", type="credit_card", starting_balance=200.0,
        ))
        # Expense on CC increases debt
        txn_repo.create(Transaction(
            account_id=cc.id, type="expense", amount=150.0,
            description="Amazon", date="2024-01-10",
        ))
        # Payment from checking TO CC (transfer) reduces debt
        txn_repo.create(Transaction(
            account_id=checking.id, type="transfer", amount=100.0,
            description="CC Payment", date="2024-01-20",
            transfer_to_account_id=cc.id,
        ))
        # CC balance: 200 + 150 - 100 = 250
        assert calc.get_balance(cc) == 250.0

    def test_empty_account_returns_starting_balance(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        acct = acct_repo.create(Account(name="Empty", type="checking", starting_balance=500.0))
        assert calc.get_balance(acct) == 500.0

    def test_empty_cc_returns_starting_balance(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        cc = acct_repo.create(Account(name="CC", type="credit_card", starting_balance=0.0))
        assert calc.get_balance(cc) == 0.0

    def test_checking_with_transfers(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        checking = acct_repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))
        savings = acct_repo.create(Account(name="Savings", type="savings", starting_balance=1000.0))
        # Transfer OUT from checking TO savings
        txn_repo.create(Transaction(
            account_id=checking.id, type="transfer", amount=500.0,
            description="To savings", date="2024-01-15",
            transfer_to_account_id=savings.id,
        ))
        # Checking: 5000 - 500 = 4500
        assert calc.get_balance(checking) == 4500.0
        # Savings: 1000 + 500 = 1500
        assert calc.get_balance(savings) == 1500.0

    def test_get_all_balances(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        checking = acct_repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))
        cc = acct_repo.create(Account(name="CC", type="credit_card", starting_balance=0.0))
        txn_repo.create(Transaction(
            account_id=cc.id, type="expense", amount=100.0,
            description="Purchase", date="2024-01-10",
        ))
        txn_repo.create(Transaction(
            account_id=checking.id, type="transfer", amount=50.0,
            description="CC Payment", date="2024-01-20",
            transfer_to_account_id=cc.id,
        ))
        balances = calc.get_all_balances()
        # Checking: 5000 - 50 = 4950
        assert balances[checking.id] == 4950.0
        # CC: 0 + 100 - 50 = 50
        assert balances[cc.id] == 50.0

    def test_mixed_transaction_types(self, conn):
        acct_repo, txn_repo, calc = self._setup(conn)
        acct = acct_repo.create(Account(name="Checking", type="checking", starting_balance=2000.0))
        txn_repo.create(Transaction(
            account_id=acct.id, type="income", amount=1000.0,
            description="Paycheck", date="2024-01-01",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=200.0,
            description="Groceries", date="2024-01-05",
        ))
        txn_repo.create(Transaction(
            account_id=acct.id, type="expense", amount=50.0,
            description="Gas", date="2024-01-10",
        ))
        # 2000 + 1000 - 200 - 50 = 2750
        assert calc.get_balance(acct) == 2750.0
