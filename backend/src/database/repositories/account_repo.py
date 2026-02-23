"""Account repository — CRUD operations for accounts."""

import sqlite3
from datetime import datetime

from src.models.account import Account


class AccountRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_account(self, row: sqlite3.Row) -> Account:
        return Account(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            starting_balance=row["starting_balance"],
            credit_limit=row["credit_limit"],
            statement_close_day=row["statement_close_day"],
            payment_due_day=row["payment_due_day"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, account: Account) -> Account:
        cursor = self.conn.execute(
            """INSERT INTO accounts (name, type, starting_balance, credit_limit,
               statement_close_day, payment_due_day)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (account.name, account.type, account.starting_balance,
             account.credit_limit, account.statement_close_day, account.payment_due_day),
        )
        self.conn.commit()
        account.id = cursor.lastrowid
        return account

    def get_by_id(self, account_id: int) -> Account | None:
        cursor = self.conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        return self._row_to_account(row) if row else None

    def get_all(self) -> list[Account]:
        cursor = self.conn.execute("SELECT * FROM accounts ORDER BY name")
        return [self._row_to_account(row) for row in cursor.fetchall()]

    def update(self, account: Account) -> Account:
        self.conn.execute(
            """UPDATE accounts SET name=?, type=?, starting_balance=?, credit_limit=?,
               statement_close_day=?, payment_due_day=?, updated_at=?
               WHERE id=?""",
            (account.name, account.type, account.starting_balance,
             account.credit_limit, account.statement_close_day, account.payment_due_day,
             datetime.now().isoformat(), account.id),
        )
        self.conn.commit()
        return account

    def delete(self, account_id: int) -> bool:
        cursor = self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()
        return cursor.rowcount > 0
