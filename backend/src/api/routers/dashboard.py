"""Dashboard endpoint — all data in one call."""

import sqlite3
from datetime import date

from fastapi import APIRouter, Depends

from src.api.deps import (
    get_account_repo,
    get_alert_service,
    get_balance_calculator,
    get_balance_sheet_service,
    get_cash_flow_service,
    get_category_repo,
    get_conn,
    get_statement_repo,
    get_transaction_repo,
)
from src.api.schemas import (
    AccountResponse,
    AlertResponse,
    BalanceSheetResponse,
    CashFlowResponse,
    DashboardResponse,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(conn: sqlite3.Connection = Depends(get_conn)):
    acct_repo = get_account_repo(conn)
    txn_repo = get_transaction_repo(conn)
    cat_repo = get_category_repo(conn)
    stmt_repo = get_statement_repo(conn)

    calc = get_balance_calculator(acct_repo, txn_repo)
    balances = calc.get_all_balances()

    accounts = acct_repo.get_all()
    account_responses = [
        AccountResponse(
            id=a.id, name=a.name, type=a.type,
            starting_balance=a.starting_balance,
            credit_limit=a.credit_limit,
            statement_close_day=a.statement_close_day,
            payment_due_day=a.payment_due_day,
            balance=balances.get(a.id, a.starting_balance),
            created_at=a.created_at, updated_at=a.updated_at,
        )
        for a in accounts
    ]

    today = date.today()
    start_of_month = today.replace(day=1).isoformat()
    end_of_month = today.isoformat()
    cf_svc = get_cash_flow_service(txn_repo, cat_repo)
    cf = cf_svc.get_cash_flow(start_of_month, end_of_month)

    alert_svc = get_alert_service(stmt_repo, acct_repo, calc, cf_svc)
    alerts = [
        AlertResponse(
            message=a.message, alert_type=a.alert_type,
            account_name=a.account_name, due_date=a.due_date,
            balance=a.balance,
        )
        for a in alert_svc.get_all_alerts()
    ]

    bs_svc = get_balance_sheet_service(acct_repo, calc)
    bs = bs_svc.get_balance_sheet()

    return DashboardResponse(
        accounts=account_responses,
        alerts=alerts,
        cash_flow=CashFlowResponse(
            total_income=cf.total_income,
            total_expenses=cf.total_expenses,
            net_cash_flow=cf.net_cash_flow,
            expenses_by_category=cf.expenses_by_category,
        ),
        balance_sheet=BalanceSheetResponse(
            assets=bs.assets, liabilities=bs.liabilities,
            total_assets=bs.total_assets,
            total_liabilities=bs.total_liabilities,
            net_worth=bs.net_worth,
        ),
    )
