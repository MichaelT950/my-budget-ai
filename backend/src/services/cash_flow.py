"""Cash flow service — income vs expenses for a period, with category breakdown."""

from dataclasses import dataclass, field

from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository


@dataclass
class CashFlowResult:
    total_income: float = 0.0
    total_expenses: float = 0.0
    net_cash_flow: float = 0.0
    expenses_by_category: dict[str, float] = field(default_factory=dict)


class CashFlowService:
    def __init__(self, transaction_repo: TransactionRepository, category_repo: CategoryRepository):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

    def get_cash_flow(
        self, start_date: str, end_date: str, account_id: int | None = None
    ) -> CashFlowResult:
        """Calculate cash flow for a period. Transfers excluded from totals."""
        if account_id is not None:
            txns = self.transaction_repo.get_by_account(account_id, start_date, end_date)
        else:
            txns = self.transaction_repo.get_all(start_date, end_date)

        categories = {c.id: c.name for c in self.category_repo.get_all()}

        total_income = 0.0
        total_expenses = 0.0
        expenses_by_cat: dict[str, float] = {}

        for txn in txns:
            if txn.type == "income":
                total_income += txn.amount
            elif txn.type == "expense":
                total_expenses += txn.amount
                cat_name = categories.get(txn.category_id, "Uncategorized")
                expenses_by_cat[cat_name] = expenses_by_cat.get(cat_name, 0) + txn.amount
            # transfers excluded

        return CashFlowResult(
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=total_income - total_expenses,
            expenses_by_category=expenses_by_cat,
        )
