"""Statement snapshot endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_conn, get_statement_repo
from src.api.schemas import StatementResponse

router = APIRouter(prefix="/api/statements", tags=["statements"])


def _stmt_response(s) -> StatementResponse:
    return StatementResponse(
        id=s.id, account_id=s.account_id,
        statement_date=s.statement_date, balance=s.balance,
        due_date=s.due_date, is_paid=s.is_paid,
        created_at=s.created_at, updated_at=s.updated_at,
    )


@router.get("", response_model=list[StatementResponse])
def list_statements(
    account_id: int | None = Query(None),
    conn: sqlite3.Connection = Depends(get_conn),
):
    repo = get_statement_repo(conn)
    if account_id is not None:
        stmts = repo.get_by_account(account_id)
    else:
        stmts = repo.get_unpaid()
    return [_stmt_response(s) for s in stmts]


@router.get("/unpaid", response_model=list[StatementResponse])
def list_unpaid_statements(conn: sqlite3.Connection = Depends(get_conn)):
    repo = get_statement_repo(conn)
    return [_stmt_response(s) for s in repo.get_unpaid()]


@router.patch("/{statement_id}/paid", response_model=dict)
def mark_statement_paid(
    statement_id: int, conn: sqlite3.Connection = Depends(get_conn)
):
    repo = get_statement_repo(conn)
    if not repo.mark_paid(statement_id):
        raise HTTPException(status_code=404, detail="Statement not found")
    return {"ok": True}
