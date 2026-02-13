"""Category repository — read-only access to predefined categories."""

import json
import sqlite3

from src.models.category import Category


class CategoryRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_category(self, row: sqlite3.Row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            keywords=json.loads(row["keywords"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_all(self) -> list[Category]:
        cursor = self.conn.execute("SELECT * FROM categories ORDER BY name")
        return [self._row_to_category(row) for row in cursor.fetchall()]

    def get_by_id(self, category_id: int) -> Category | None:
        cursor = self.conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return self._row_to_category(row) if row else None

    def get_by_name(self, name: str) -> Category | None:
        cursor = self.conn.execute("SELECT * FROM categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        return self._row_to_category(row) if row else None
