"""Balance sheet service — assets, liabilities, net worth."""

from dataclasses import dataclass, field

from src.database.repositories.account_repo import AccountRepository
from src.services.balance_calculator import BalanceCalculator


@dataclass
class BalanceSheetResult:
    assets: dict[str, float] = field(default_factory=dict)
    liabilities: dict[str, float] = field(default_factory=dict)
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    net_worth: float = 0.0


class BalanceSheetService:
    def __init__(self, account_repo: AccountRepository, balance_calculator: BalanceCalculator):
        self.account_repo = account_repo
        self.balance_calculator = balance_calculator

    def get_balance_sheet(self) -> BalanceSheetResult:
        accounts = self.account_repo.get_all()
        balances = self.balance_calculator.get_all_balances()

        assets = {}
        liabilities = {}

        for acct in accounts:
            balance = balances.get(acct.id, 0)
            if acct.type == "credit_card":
                liabilities[acct.name] = balance
            else:
                assets[acct.name] = balance

        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())

        return BalanceSheetResult(
            assets=assets,
            liabilities=liabilities,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets - total_liabilities,
        )
