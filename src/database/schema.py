"""Database schema initialization — CREATE TABLE and indexes."""

import sqlite3


def initialize_database(conn: sqlite3.Connection):
    """Create all tables and indexes. Idempotent (IF NOT EXISTS)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('credit_card', 'checking', 'savings')),
            starting_balance REAL NOT NULL DEFAULT 0,
            credit_limit REAL,
            statement_close_day INTEGER CHECK(statement_close_day BETWEEN 1 AND 31),
            payment_due_day INTEGER CHECK(payment_due_day BETWEEN 1 AND 31),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL,
            keywords TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL REFERENCES accounts(id),
            type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'transfer')),
            amount REAL NOT NULL CHECK(amount > 0),
            description TEXT NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            date TEXT NOT NULL,
            transfer_to_account_id INTEGER REFERENCES accounts(id),
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS statement_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL REFERENCES accounts(id),
            statement_date TEXT NOT NULL,
            balance REAL NOT NULL,
            due_date TEXT NOT NULL,
            is_paid INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, statement_date)
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
        CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
        CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
        CREATE INDEX IF NOT EXISTS idx_statement_snapshots_account_id ON statement_snapshots(account_id);
        CREATE INDEX IF NOT EXISTS idx_statement_snapshots_due_date ON statement_snapshots(due_date);
    """)
