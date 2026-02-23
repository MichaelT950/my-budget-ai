"""Transaction endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_categorizer, get_category_repo, get_conn, get_transaction_repo
from src.api.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from src.models.transaction import Transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _txn_response(t: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=t.id, account_id=t.account_id, type=t.type,
        amount=t.amount, description=t.description,
        category_id=t.category_id, date=t.date,
        transfer_to_account_id=t.transfer_to_account_id,
        notes=t.notes,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    account_id: int | None = Query(None),
    conn: sqlite3.Connection = Depends(get_conn),
):
    repo = get_transaction_repo(conn)
    if account_id is not None:
        txns = repo.get_by_account(account_id, start_date, end_date)
    else:
        txns = repo.get_all(start_date, end_date)
    return [_txn_response(t) for t in txns]


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    body: TransactionCreate, conn: sqlite3.Connection = Depends(get_conn)
):
    repo = get_transaction_repo(conn)
    cat_repo = get_category_repo(conn)

    category_id = body.category_id
    if category_id is None and body.type == "expense":
        categorizer = get_categorizer(cat_repo)
        cat = categorizer.categorize_with_fallback(body.description)
        category_id = cat.id

    txn = repo.create(Transaction(
        account_id=body.account_id, type=body.type,
        amount=body.amount, description=body.description,
        category_id=category_id, date=body.date,
        transfer_to_account_id=body.transfer_to_account_id,
        notes=body.notes,
    ))
    return _txn_response(txn)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int, body: TransactionUpdate,
    conn: sqlite3.Connection = Depends(get_conn),
):
    repo = get_transaction_repo(conn)
    txns = repo.get_all()
    txn = next((t for t in txns if t.id == transaction_id), None)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if body.account_id is not None:
        txn.account_id = body.account_id
    if body.type is not None:
        txn.type = body.type
    if body.amount is not None:
        txn.amount = body.amount
    if body.description is not None:
        txn.description = body.description
    if body.category_id is not None:
        txn.category_id = body.category_id
    if body.date is not None:
        txn.date = body.date
    if body.transfer_to_account_id is not None:
        txn.transfer_to_account_id = body.transfer_to_account_id
    if body.notes is not None:
        txn.notes = body.notes

    repo.update(txn)
    return _txn_response(txn)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int, conn: sqlite3.Connection = Depends(get_conn)
):
    repo = get_transaction_repo(conn)
    if not repo.delete(transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
