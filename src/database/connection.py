"""Singleton SQLite connection manager."""

import sqlite3

_connection: sqlite3.Connection | None = None


def get_connection(db_path: str = "data/budget.db") -> sqlite3.Connection:
    """Get or create a singleton database connection.

    Enables WAL mode and foreign keys. Accepts ':memory:' for tests.
    """
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(db_path)
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
        _connection.row_factory = sqlite3.Row
    return _connection


def close_connection():
    """Close the singleton connection if open."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def reset_connection():
    """Reset the singleton (close and clear). Useful for tests."""
    close_connection()
