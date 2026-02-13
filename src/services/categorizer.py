"""Auto-categorization service — keyword-based category matching."""

from src.models.category import Category


class Categorizer:
    """Maps transaction descriptions to categories using keyword substring matching."""

    def __init__(self, categories: list[Category]):
        self._categories = categories
        self._keyword_map: list[tuple[str, Category]] = []
        self._uncategorized: Category | None = None
        for cat in categories:
            if cat.name == "Uncategorized":
                self._uncategorized = cat
            for keyword in cat.keywords:
                self._keyword_map.append((keyword.lower(), cat))

    def categorize(self, description: str) -> Category | None:
        """Return matching category or None if no keyword matches."""
        desc_lower = description.lower()
        for keyword, category in self._keyword_map:
            if keyword in desc_lower:
                return category
        return None

    def categorize_with_fallback(self, description: str) -> Category:
        """Return matching category, or Uncategorized if no match."""
        result = self.categorize(description)
        if result is not None:
            return result
        if self._uncategorized is not None:
            return self._uncategorized
        return Category(name="Uncategorized", color="gray")
