"""CSV import endpoints."""

import io
import sqlite3

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.api.deps import (
    get_categorizer,
    get_category_repo,
    get_conn,
    get_csv_importer,
    get_transaction_repo,
)
from src.api.schemas import (
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    ImportPreviewTransaction,
)
from src.models.transaction import Transaction

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_import(
    file: UploadFile = File(...),
    account_id: int = Form(...),
    conn: sqlite3.Connection = Depends(get_conn),
):
    contents = await file.read()
    file_like = io.StringIO(contents.decode("utf-8"))

    importer = get_csv_importer()
    result = importer.import_csv(file_like, account_id)

    cat_repo = get_category_repo(conn)
    categorizer = get_categorizer(cat_repo)

    preview_txns = []
    for t in result.transactions:
        if t.type == "expense" and not t.category_id:
            cat = categorizer.categorize_with_fallback(t.description)
            t.category_id = cat.id
        preview_txns.append(ImportPreviewTransaction(
            account_id=t.account_id, type=t.type,
            amount=t.amount, description=t.description,
            date=t.date,
        ))

    return ImportPreviewResponse(
        transactions=preview_txns,
        errors=result.errors,
        total_rows=result.total_rows,
    )


@router.post("/confirm", response_model=ImportConfirmResponse)
def confirm_import(
    body: ImportConfirmRequest,
    conn: sqlite3.Connection = Depends(get_conn),
):
    txn_repo = get_transaction_repo(conn)
    cat_repo = get_category_repo(conn)
    categorizer = get_categorizer(cat_repo)

    transactions = []
    for t in body.transactions:
        category_id = None
        if t.type == "expense":
            cat = categorizer.categorize_with_fallback(t.description)
            category_id = cat.id

        transactions.append(Transaction(
            account_id=body.account_id, type=t.type,
            amount=t.amount, description=t.description,
            category_id=category_id, date=t.date,
        ))

    txn_repo.create_many(transactions)
    return ImportConfirmResponse(imported_count=len(transactions))
