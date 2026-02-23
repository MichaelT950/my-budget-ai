"""Alert service — payment due dates, overdraft warnings, expense threshold."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository
from src.services.balance_calculator import BalanceCalculator
from src.services.cash_flow import CashFlowService


@dataclass
class Alert:
    message: str
    alert_type: str = "warning"  # warning, info, error
    account_name: str = ""
    due_date: str = ""
    balance: float = 0.0


class AlertService:
    def __init__(
        self,
        statement_repo: StatementRepository,
        account_repo: AccountRepository,
        balance_calculator: BalanceCalculator,
        cash_flow_service: CashFlowService,
    ):
        self.statement_repo = statement_repo
        self.account_repo = account_repo
        self.balance_calculator = balance_calculator
        self.cash_flow_service = cash_flow_service

    def get_due_date_alerts(self) -> list[Alert]:
        """Get alerts for unpaid statements due within 7 days."""
        unpaid = self.statement_repo.get_unpaid()
        accounts = {a.id: a for a in self.account_repo.get_all()}
        today = date.today()
        window_end = today + timedelta(days=7)
        alerts = []

        for stmt in unpaid:
            try:
                due = date.fromisoformat(stmt.due_date)
            except ValueError:
                continue

            if today <= due <= window_end:
                acct = accounts.get(stmt.account_id)
                acct_name = acct.name if acct else "Unknown"
                days_left = (due - today).days
                day_word = "day" if days_left == 1 else "days"

                alerts.append(Alert(
                    message=f"{acct_name}: ${stmt.balance:,.2f} due in {days_left} {day_word} ({stmt.due_date})",
                    alert_type="warning",
                    account_name=acct_name,
                    due_date=stmt.due_date,
                    balance=stmt.balance,
                ))

        return alerts

    def get_overdraft_alerts(self) -> list[Alert]:
        """Warn when a checking/savings account balance is negative (overdraft)."""
        accounts = self.account_repo.get_all()
        balances = self.balance_calculator.get_all_balances()
        alerts = []

        for acct in accounts:
            if acct.type == "credit_card":
                continue
            balance = balances.get(acct.id, acct.starting_balance)
            if balance < 0:
                alerts.append(Alert(
                    message=f"{acct.name}: balance is -${abs(balance):,.2f} (overdraft)",
                    alert_type="error",
                    account_name=acct.name,
                    balance=balance,
                ))

        return alerts

    def get_expense_threshold_alerts(self) -> list[Alert]:
        """Warn when current-month expenses reach 90% or more of income."""
        today = date.today()
        start_of_month = today.replace(day=1).isoformat()
        end_of_month = today.isoformat()

        cf = self.cash_flow_service.get_cash_flow(start_of_month, end_of_month)

        if cf.total_income <= 0:
            return []

        ratio = cf.total_expenses / cf.total_income
        if ratio >= 0.9:
            pct = int(ratio * 100)
            alerts = [Alert(
                message=f"Expenses are {pct}% of income this month (${cf.total_expenses:,.2f} / ${cf.total_income:,.2f})",
                alert_type="warning" if ratio < 1.0 else "error",
            )]
            return alerts

        return []

    def get_all_alerts(self) -> list[Alert]:
        """Get all alerts: due dates, overdrafts, and expense thresholds."""
        alerts = []
        alerts.extend(self.get_due_date_alerts())
        alerts.extend(self.get_overdraft_alerts())
        alerts.extend(self.get_expense_threshold_alerts())
        return alerts
