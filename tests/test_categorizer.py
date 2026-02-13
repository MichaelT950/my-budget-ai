"""Tests for Categorizer — keyword matching, case insensitivity, fallback."""

from src.database.repositories.category_repo import CategoryRepository
from src.services.categorizer import Categorizer


class TestCategorizer:
    def test_keyword_match(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("WHOLE FOODS GROCERY STORE")
        assert result is not None
        assert result.name == "Food & Drink"

    def test_case_insensitive(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("amazon purchase")
        assert result is not None
        assert result.name == "Shopping"

    def test_multi_word_keyword(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("UBER EATS delivery")
        assert result is not None
        assert result.name == "Food & Drink"

    def test_no_match_returns_none(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        assert cat.categorize("RANDOM VENDOR XYZ") is None

    def test_fallback_returns_uncategorized(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize_with_fallback("RANDOM VENDOR XYZ")
        assert result.name == "Uncategorized"

    def test_health_category(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("CVS PHARMACY #1234")
        assert result is not None
        assert result.name == "Health"

    def test_transportation(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("SHELL GAS STATION")
        assert result is not None
        assert result.name == "Transportation"

    def test_services(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("NETFLIX SUBSCRIPTION")
        assert result is not None
        assert result.name == "Services"

    def test_entertainment(self, conn):
        categories = CategoryRepository(conn).get_all()
        cat = Categorizer(categories)
        result = cat.categorize("STEAM PURCHASE")
        assert result is not None
        assert result.name == "Entertainment"
