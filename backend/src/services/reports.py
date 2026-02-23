"""Report service — weekly/monthly/yearly summaries with category drill-down."""

from dataclasses import dataclass, field
from datetime import date, timedelta

from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository


@dataclass
class CategorySummary:
    name: str = ""
    total: float = 0.0
    count: int = 0
    transactions: list = field(default_factory=list)


@dataclass
class PeriodSummary:
    period_label: str = ""
    start_date: str = ""
    end_date: str = ""
    total_income: float = 0.0
    total_expenses: float = 0.0
    net: float = 0.0
    top_category: str = ""
    expenses_by_category: list[CategorySummary] = field(default_factory=list)


class ReportService:
    def __init__(self, transaction_repo: TransactionRepository, category_repo: CategoryRepository):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

    def get_period_summary(self, start_date: str, end_date: str) -> PeriodSummary:
        """Get summary for an arbitrary date range."""
        txns = self.transaction_repo.get_all(start_date, end_date)
        categories = {c.id: c.name for c in self.category_repo.get_all()}

        total_income = 0.0
        total_expenses = 0.0
        cat_data: dict[str, CategorySummary] = {}

        for txn in txns:
            if txn.type == "income":
                total_income += txn.amount
            elif txn.type == "expense":
                total_expenses += txn.amount
                cat_name = categories.get(txn.category_id, "Uncategorized")
                if cat_name not in cat_data:
                    cat_data[cat_name] = CategorySummary(name=cat_name)
                cat_data[cat_name].total += txn.amount
                cat_data[cat_name].count += 1
                cat_data[cat_name].transactions.append(txn)

        sorted_cats = sorted(cat_data.values(), key=lambda c: c.total, reverse=True)
        top_category = sorted_cats[0].name if sorted_cats else ""

        return PeriodSummary(
            start_date=start_date,
            end_date=end_date,
            total_income=total_income,
            total_expenses=total_expenses,
            net=total_income - total_expenses,
            top_category=top_category,
            expenses_by_category=sorted_cats,
        )

    def get_monthly_summary(self, year: int, month: int) -> PeriodSummary:
        """Get summary for a specific month."""
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        summary = self.get_period_summary(start.isoformat(), end.isoformat())
        summary.period_label = start.strftime("%B %Y")
        return summary

    def get_weekly_summary(self, week_start: date) -> PeriodSummary:
        """Get summary for a week starting on week_start (Monday)."""
        end = week_start + timedelta(days=6)
        summary = self.get_period_summary(week_start.isoformat(), end.isoformat())
        summary.period_label = f"Week of {week_start.isoformat()}"
        return summary
