"""Balance calculation service — computes account balances from transactions."""

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account


class BalanceCalculator:
    """Compute current balances for accounts based on their transactions.

    Checking/Savings: starting_balance + income + transfers_in - expenses - transfers_out
    Credit Card: starting_balance + expenses - payments_received (transfers IN to CC)
    """

    def __init__(self, account_repo: AccountRepository, transaction_repo: TransactionRepository):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    def get_balance(self, account: Account) -> float:
        """Calculate current balance for a single account."""
        txns = self.transaction_repo.get_by_account(account.id)

        if account.type == "credit_card":
            return self._calc_credit_card_balance(account, txns)
        return self._calc_checking_savings_balance(account, txns)

    def get_all_balances(self) -> dict[int, float]:
        """Calculate balances for all accounts. Returns {account_id: balance}."""
        accounts = self.account_repo.get_all()
        all_txns = self.transaction_repo.get_all()

        # Also need transfers INTO each account (where transfer_to_account_id = account.id)
        # These won't show up in get_by_account since that filters on account_id
        result = {}
        for account in accounts:
            account_txns = [t for t in all_txns if t.account_id == account.id]
            transfers_in = [t for t in all_txns
                            if t.type == "transfer" and t.transfer_to_account_id == account.id]

            if account.type == "credit_card":
                balance = self._calc_cc_with_transfers_in(account, account_txns, transfers_in)
            else:
                balance = self._calc_cs_with_transfers_in(account, account_txns, transfers_in)
            result[account.id] = balance
        return result

    def _calc_credit_card_balance(self, account: Account, txns: list) -> float:
        """CC balance = starting_balance + expenses - transfers_in (payments)."""
        expenses = sum(t.amount for t in txns if t.type == "expense")
        # Transfers IN to this CC reduce debt — but get_by_account only returns
        # transactions where account_id matches, not transfer_to_account_id.
        # For single-account calc, we need a separate query.
        all_txns = self.transaction_repo.get_all()
        transfers_in = sum(
            t.amount for t in all_txns
            if t.type == "transfer" and t.transfer_to_account_id == account.id
        )
        return account.starting_balance + expenses - transfers_in

    def _calc_checking_savings_balance(self, account: Account, txns: list) -> float:
        """Checking/Savings = starting + income + transfers_in - expenses - transfers_out."""
        income = sum(t.amount for t in txns if t.type == "income")
        expenses = sum(t.amount for t in txns if t.type == "expense")
        transfers_out = sum(t.amount for t in txns if t.type == "transfer")

        all_txns = self.transaction_repo.get_all()
        transfers_in = sum(
            t.amount for t in all_txns
            if t.type == "transfer" and t.transfer_to_account_id == account.id
        )
        return account.starting_balance + income + transfers_in - expenses - transfers_out

    def _calc_cc_with_transfers_in(self, account: Account, account_txns: list, transfers_in: list) -> float:
        expenses = sum(t.amount for t in account_txns if t.type == "expense")
        payments = sum(t.amount for t in transfers_in)
        return account.starting_balance + expenses - payments

    def _calc_cs_with_transfers_in(self, account: Account, account_txns: list, transfers_in: list) -> float:
        income = sum(t.amount for t in account_txns if t.type == "income")
        expenses = sum(t.amount for t in account_txns if t.type == "expense")
        transfers_out = sum(t.amount for t in account_txns if t.type == "transfer")
        transfers_in_total = sum(t.amount for t in transfers_in)
        return account.starting_balance + income + transfers_in_total - expenses - transfers_out
