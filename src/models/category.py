"""Category model — expense categories with color coding and keyword rules."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Category:
    id: int | None = None
    name: str = ""
    color: str = ""
    keywords: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
