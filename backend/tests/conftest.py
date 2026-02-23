"""Shared pytest fixtures — fresh :memory: SQLite per test."""

import sqlite3

import pytest

from src.database.schema import initialize_database
from src.database.seeds import seed_categories


@pytest.fixture
def conn():
    """Provide a fresh in-memory SQLite connection with schema + seeded categories."""
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.row_factory = sqlite3.Row
    initialize_database(connection)
    seed_categories(connection)
    yield connection
    connection.close()
