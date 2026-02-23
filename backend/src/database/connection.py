"""SQLite connection factory."""

import sqlite3


def create_connection(db_path: str = "data/budget.db") -> sqlite3.Connection:
    """Create a new database connection.

    Enables WAL mode and foreign keys. Accepts ':memory:' for tests.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


# Backwards-compatible aliases used by existing code and tests
_connection: sqlite3.Connection | None = None


def get_connection(db_path: str = "data/budget.db") -> sqlite3.Connection:
    """Get or create a singleton database connection (legacy)."""
    global _connection
    if _connection is None:
        _connection = create_connection(db_path)
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
