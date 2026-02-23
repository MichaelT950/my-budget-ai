"""Report endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, Query

from src.api.deps import (
    get_account_repo,
    get_balance_calculator,
    get_balance_sheet_service,
    get_cash_flow_service,
    get_category_repo,
    get_conn,
    get_report_service,
    get_transaction_repo,
)
from src.api.schemas import (
    BalanceSheetResponse,
    CashFlowResponse,
    CategorySummaryResponse,
    PeriodSummaryResponse,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/cash-flow", response_model=CashFlowResponse)
def get_cash_flow(
    start_date: str = Query(...),
    end_date: str = Query(...),
    account_id: int | None = Query(None),
    conn: sqlite3.Connection = Depends(get_conn),
):
    txn_repo = get_transaction_repo(conn)
    cat_repo = get_category_repo(conn)
    svc = get_cash_flow_service(txn_repo, cat_repo)
    cf = svc.get_cash_flow(start_date, end_date, account_id)
    return CashFlowResponse(
        total_income=cf.total_income,
        total_expenses=cf.total_expenses,
        net_cash_flow=cf.net_cash_flow,
        expenses_by_category=cf.expenses_by_category,
    )


@router.get("/balance-sheet", response_model=BalanceSheetResponse)
def get_balance_sheet(conn: sqlite3.Connection = Depends(get_conn)):
    acct_repo = get_account_repo(conn)
    txn_repo = get_transaction_repo(conn)
    calc = get_balance_calculator(acct_repo, txn_repo)
    svc = get_balance_sheet_service(acct_repo, calc)
    bs = svc.get_balance_sheet()
    return BalanceSheetResponse(
        assets=bs.assets, liabilities=bs.liabilities,
        total_assets=bs.total_assets,
        total_liabilities=bs.total_liabilities,
        net_worth=bs.net_worth,
    )


@router.get("/period-summary", response_model=PeriodSummaryResponse)
def get_period_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    conn: sqlite3.Connection = Depends(get_conn),
):
    txn_repo = get_transaction_repo(conn)
    cat_repo = get_category_repo(conn)
    svc = get_report_service(txn_repo, cat_repo)
    summary = svc.get_period_summary(start_date, end_date)
    return PeriodSummaryResponse(
        period_label=summary.period_label,
        start_date=summary.start_date,
        end_date=summary.end_date,
        total_income=summary.total_income,
        total_expenses=summary.total_expenses,
        net=summary.net,
        top_category=summary.top_category,
        expenses_by_category=[
            CategorySummaryResponse(name=c.name, total=c.total, count=c.count)
            for c in summary.expenses_by_category
        ],
    )
