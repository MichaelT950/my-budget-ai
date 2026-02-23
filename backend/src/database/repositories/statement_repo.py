"""Statement snapshot repository — CRUD for credit card statements."""

import sqlite3
from datetime import datetime

from src.models.statement import StatementSnapshot


class StatementRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_snapshot(self, row: sqlite3.Row) -> StatementSnapshot:
        return StatementSnapshot(
            id=row["id"],
            account_id=row["account_id"],
            statement_date=row["statement_date"],
            balance=row["balance"],
            due_date=row["due_date"],
            is_paid=bool(row["is_paid"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, snapshot: StatementSnapshot) -> StatementSnapshot:
        cursor = self.conn.execute(
            """INSERT INTO statement_snapshots (account_id, statement_date, balance,
               due_date, is_paid)
               VALUES (?, ?, ?, ?, ?)""",
            (snapshot.account_id, snapshot.statement_date, snapshot.balance,
             snapshot.due_date, int(snapshot.is_paid)),
        )
        self.conn.commit()
        snapshot.id = cursor.lastrowid
        return snapshot

    def get_by_account(self, account_id: int) -> list[StatementSnapshot]:
        cursor = self.conn.execute(
            "SELECT * FROM statement_snapshots WHERE account_id = ? ORDER BY statement_date DESC",
            (account_id,),
        )
        return [self._row_to_snapshot(row) for row in cursor.fetchall()]

    def get_unpaid(self) -> list[StatementSnapshot]:
        cursor = self.conn.execute(
            "SELECT * FROM statement_snapshots WHERE is_paid = 0 ORDER BY due_date"
        )
        return [self._row_to_snapshot(row) for row in cursor.fetchall()]

    def mark_paid(self, snapshot_id: int) -> bool:
        cursor = self.conn.execute(
            "UPDATE statement_snapshots SET is_paid = 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), snapshot_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0
