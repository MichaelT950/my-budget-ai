"""Transaction repository — CRUD with date range filtering."""

import sqlite3
from datetime import datetime

from src.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        return Transaction(
            id=row["id"],
            account_id=row["account_id"],
            type=row["type"],
            amount=row["amount"],
            description=row["description"],
            category_id=row["category_id"],
            date=row["date"],
            transfer_to_account_id=row["transfer_to_account_id"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, txn: Transaction) -> Transaction:
        cursor = self.conn.execute(
            """INSERT INTO transactions (account_id, type, amount, description,
               category_id, date, transfer_to_account_id, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (txn.account_id, txn.type, txn.amount, txn.description,
             txn.category_id, txn.date, txn.transfer_to_account_id, txn.notes),
        )
        self.conn.commit()
        txn.id = cursor.lastrowid
        return txn

    def create_many(self, transactions: list[Transaction]) -> list[Transaction]:
        for txn in transactions:
            cursor = self.conn.execute(
                """INSERT INTO transactions (account_id, type, amount, description,
                   category_id, date, transfer_to_account_id, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (txn.account_id, txn.type, txn.amount, txn.description,
                 txn.category_id, txn.date, txn.transfer_to_account_id, txn.notes),
            )
            txn.id = cursor.lastrowid
        self.conn.commit()
        return transactions

    def get_by_account(
        self, account_id: int, start_date: str | None = None, end_date: str | None = None
    ) -> list[Transaction]:
        query = "SELECT * FROM transactions WHERE account_id = ?"
        params: list = [account_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date DESC"
        cursor = self.conn.execute(query, params)
        return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def get_all(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> list[Transaction]:
        query = "SELECT * FROM transactions WHERE 1=1"
        params: list = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date DESC"
        cursor = self.conn.execute(query, params)
        return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def update(self, txn: Transaction) -> Transaction:
        self.conn.execute(
            """UPDATE transactions SET account_id=?, type=?, amount=?, description=?,
               category_id=?, date=?, transfer_to_account_id=?, notes=?, updated_at=?
               WHERE id=?""",
            (txn.account_id, txn.type, txn.amount, txn.description,
             txn.category_id, txn.date, txn.transfer_to_account_id, txn.notes,
             datetime.now().isoformat(), txn.id),
        )
        self.conn.commit()
        return txn

    def delete(self, transaction_id: int) -> bool:
        cursor = self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def find_duplicates(
        self, account_id: int, transactions: list[Transaction]
    ) -> list[bool]:
        """Check which transactions already exist (by account_id + date + amount + description).

        Returns a list of booleans parallel to the input list — True means duplicate.
        """
        results = []
        for txn in transactions:
            cursor = self.conn.execute(
                """SELECT COUNT(*) FROM transactions
                   WHERE account_id = ? AND date = ? AND amount = ? AND description = ?""",
                (account_id, txn.date, txn.amount, txn.description),
            )
            results.append(cursor.fetchone()[0] > 0)
        return results
