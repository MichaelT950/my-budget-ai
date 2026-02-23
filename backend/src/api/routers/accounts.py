"""Account endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import (
    get_account_repo,
    get_balance_calculator,
    get_conn,
    get_transaction_repo,
)
from src.api.schemas import AccountCreate, AccountResponse, AccountUpdate
from src.models.account import Account

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountResponse])
def list_accounts(conn: sqlite3.Connection = Depends(get_conn)):
    acct_repo = get_account_repo(conn)
    txn_repo = get_transaction_repo(conn)
    calc = get_balance_calculator(acct_repo, txn_repo)
    accounts = acct_repo.get_all()
    balances = calc.get_all_balances()
    return [
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


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    body: AccountCreate, conn: sqlite3.Connection = Depends(get_conn)
):
    repo = get_account_repo(conn)
    account = repo.create(Account(
        name=body.name, type=body.type,
        starting_balance=body.starting_balance,
        credit_limit=body.credit_limit,
        statement_close_day=body.statement_close_day,
        payment_due_day=body.payment_due_day,
    ))
    return AccountResponse(
        id=account.id, name=account.name, type=account.type,
        starting_balance=account.starting_balance,
        credit_limit=account.credit_limit,
        statement_close_day=account.statement_close_day,
        payment_due_day=account.payment_due_day,
        balance=account.starting_balance,
        created_at=account.created_at, updated_at=account.updated_at,
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    acct_repo = get_account_repo(conn)
    txn_repo = get_transaction_repo(conn)
    calc = get_balance_calculator(acct_repo, txn_repo)
    account = acct_repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    balance = calc.get_balance(account)
    return AccountResponse(
        id=account.id, name=account.name, type=account.type,
        starting_balance=account.starting_balance,
        credit_limit=account.credit_limit,
        statement_close_day=account.statement_close_day,
        payment_due_day=account.payment_due_day,
        balance=balance,
        created_at=account.created_at, updated_at=account.updated_at,
    )


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int, body: AccountUpdate,
    conn: sqlite3.Connection = Depends(get_conn),
):
    repo = get_account_repo(conn)
    account = repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.name = body.name
    account.type = body.type
    account.starting_balance = body.starting_balance
    account.credit_limit = body.credit_limit
    account.statement_close_day = body.statement_close_day
    account.payment_due_day = body.payment_due_day
    repo.update(account)
    return AccountResponse(
        id=account.id, name=account.name, type=account.type,
        starting_balance=account.starting_balance,
        credit_limit=account.credit_limit,
        statement_close_day=account.statement_close_day,
        payment_due_day=account.payment_due_day,
        created_at=account.created_at, updated_at=account.updated_at,
    )


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: int, conn: sqlite3.Connection = Depends(get_conn)
):
    repo = get_account_repo(conn)
    if not repo.delete(account_id):
        raise HTTPException(status_code=404, detail="Account not found")
