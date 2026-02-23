"""Seed data — predefined categories with colors and keywords."""

import json
import sqlite3


def seed_categories(conn: sqlite3.Connection):
    """Insert default categories. Idempotent via INSERT OR IGNORE."""
    categories = [
        ("Health", "red", ["doctor", "pharmacy", "medical", "hospital", "clinic", "dental", "vision", "health"]),
        ("Food & Drink", "orange", ["grocery", "restaurant", "uber eats", "doordash", "grubhub", "starbucks", "coffee", "food"]),
        ("Shopping", "yellow", ["amazon", "target", "walmart", "clothing", "electronics", "store", "shop", "retail"]),
        ("Travel", "green", ["airline", "hotel", "airbnb", "booking", "flight", "vacation", "travel", "trip"]),
        ("Transportation", "blue", ["gas", "uber", "lyft", "parking", "transit", "metro", "fuel", "car", "auto"]),
        ("Services", "purple", ["utility", "subscription", "netflix", "spotify", "electric", "water", "internet", "phone"]),
        ("Entertainment", "pink", ["movie", "theater", "concert", "gaming", "steam", "playstation", "xbox", "hulu"]),
        ("Uncategorized", "gray", []),
    ]
    for name, color, keywords in categories:
        conn.execute(
            "INSERT OR IGNORE INTO categories (name, color, keywords) VALUES (?, ?, ?)",
            (name, color, json.dumps(keywords)),
        )
    conn.commit()
