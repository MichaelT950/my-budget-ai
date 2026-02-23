"""Category endpoints."""

import sqlite3

from fastapi import APIRouter, Depends

from src.api.deps import get_category_repo, get_conn
from src.api.schemas import CategoryResponse
from src.database.repositories.category_repo import CategoryRepository

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    conn: sqlite3.Connection = Depends(get_conn),
):
    repo = get_category_repo(conn)
    categories = repo.get_all()
    return [
        CategoryResponse(
            id=c.id,
            name=c.name,
            color=c.color,
            keywords=c.keywords,
        )
        for c in categories
    ]
