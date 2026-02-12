# Project Structure

## Directory Layout

```
my-budget-ai/
├── spec/                          # Specification documents
│   ├── README.md                  # Main specification
│   ├── DATA_MODEL.md              # Database schema and queries
│   └── PROJECT_STRUCTURE.md       # This file
│
├── src/                           # Application source code
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   │
│   ├── models/                    # Data models (dataclasses)
│   │   ├── __init__.py
│   │   ├── account.py             # Account model
│   │   ├── transaction.py         # Transaction model
│   │   ├── category.py            # Category model
│   │   └── statement.py           # StatementSnapshot model
│   │
│   ├── database/                  # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py          # SQLite connection management
│   │   ├── schema.py              # Table creation and migrations
│   │   ├── seeds.py               # Seed data (categories)
│   │   └── repositories/          # Data access layer
│   │       ├── __init__.py
│   │       ├── account_repo.py    # Account CRUD operations
│   │       ├── transaction_repo.py # Transaction CRUD operations
│   │       ├── category_repo.py   # Category operations
│   │       └── statement_repo.py  # Statement snapshot operations
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── categorizer.py         # Rule-based auto-categorization
│   │   ├── importer.py            # CSV import logic
│   │   ├── balance_calculator.py  # Account balance calculations
│   │   ├── cash_flow.py           # Cash flow statement logic
│   │   ├── balance_sheet.py       # Balance sheet (net worth) logic
│   │   ├── alerts.py              # Due date and overdraft warnings
│   │   └── reports.py             # Activity analysis and exports
│   │
│   ├── ui/                        # Tkinter GUI layer
│   │   ├── __init__.py
│   │   ├── app.py                 # Main application window
│   │   ├── theme.py               # Colors and styling constants
│   │   ├── components/            # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── alert_banner.py    # Warning/alert display
│   │   │   └── data_table.py      # Transaction list table
│   │   └── views/                 # Application views/screens
│   │       ├── __init__.py
│   │       ├── dashboard.py       # Main dashboard (combined view)
│   │       ├── accounts.py        # Account management view
│   │       ├── transactions.py    # Transaction list/search view
│   │       ├── import_csv.py      # CSV import wizard
│   │       └── reports.py         # Reports and analysis view
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── date_helpers.py        # Date parsing and formatting
│       └── formatters.py          # Currency and number formatting
│
├── data/                          # Data directory (gitignored except .gitkeep)
│   ├── .gitkeep
│   └── budget.db                  # SQLite database (created at runtime)
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures
│   ├── test_categorizer.py
│   ├── test_importer.py
│   ├── test_balance_calculator.py
│   └── test_repositories.py
│
├── sample_data/                   # Sample CSV files for testing
│   └── sample_transactions.csv
│
├── pyproject.toml                 # Project configuration
├── README.md                      # User-facing readme
└── .gitignore
```

---

## Module Responsibilities

### `src/main.py`
- Application entry point
- Initialize database connection
- Launch Tkinter main window
- Handle graceful shutdown

### `src/models/`
Python dataclasses representing domain entities. No database logic here.

```python
# Example: src/models/account.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Account:
    id: Optional[int]
    name: str
    type: str  # 'credit_card', 'checking', 'savings'
    starting_balance: float
    credit_limit: Optional[float] = None
    statement_close_day: Optional[int] = None
    payment_due_day: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### `src/database/`
All SQLite interactions isolated here.

- **connection.py**: Singleton connection, context manager
- **schema.py**: CREATE TABLE statements, migrations
- **seeds.py**: Insert default categories
- **repositories/**: CRUD operations returning model objects

### `src/services/`
Business logic, independent of UI and database implementation.

- **categorizer.py**: Match transaction descriptions to categories
- **importer.py**: Parse CSV, validate, create transactions
- **balance_calculator.py**: Compute account balances
- **cash_flow.py**: Income vs expenses for period
- **balance_sheet.py**: Net worth calculation
- **alerts.py**: Check for upcoming due dates, overdraft risks
- **reports.py**: Generate activity analysis data

### `src/ui/`
Tkinter GUI code.

- **app.py**: Main window, menu bar, view navigation
- **theme.py**: Category colors, fonts, spacing
- **components/**: Reusable widgets
- **views/**: Full-screen views (dashboard, accounts, etc.)

### `src/utils/`
Stateless helper functions.

---

## Key Design Decisions

### 1. Layered Architecture
```
UI (Tkinter) → Services (Business Logic) → Repositories (Data Access) → SQLite
```
Each layer only depends on the layer below it.

### 2. Repository Pattern
Database operations are encapsulated in repository classes, returning model objects. This makes testing easier and keeps SQL out of business logic.

### 3. Dataclasses for Models
Simple, immutable-ish data containers. No ORM complexity.

### 4. Single Database File
All data in `data/budget.db`. Easy backup (copy the file).

### 5. Category Colors in Theme
```python
# src/ui/theme.py
CATEGORY_COLORS = {
    'red': '#E53935',      # Health
    'orange': '#FB8C00',   # Food & Drink
    'yellow': '#FDD835',   # Shopping
    'green': '#43A047',    # Travel
    'blue': '#1E88E5',     # Transportation
    'purple': '#8E24AA',   # Services
    'pink': '#D81B60',     # Entertainment
    'gray': '#757575',     # Uncategorized
}
```

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `balance_calculator.py` |
| Classes | PascalCase | `AccountRepository` |
| Functions | snake_case | `calculate_balance()` |
| Constants | UPPER_SNAKE | `CATEGORY_COLORS` |

---

## Import Examples

```python
# In a service
from src.models.transaction import Transaction
from src.database.repositories.transaction_repo import TransactionRepository

# In a view
from src.services.cash_flow import CashFlowService
from src.ui.theme import CATEGORY_COLORS
```

---

## Database Location

The SQLite database is stored at:
```
my-budget-ai/data/budget.db
```

On first run, the application will:
1. Create the `data/` directory if it doesn't exist
2. Create `budget.db` with all tables
3. Seed the categories table with default values

---

## Configuration

All configuration in `pyproject.toml`:

```toml
[project]
name = "my-budget-ai"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "matplotlib>=3.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "W"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## Running the Application

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .

# Run the app
python -m src.main

# Run tests
pytest

# Lint
ruff check src/ tests/
```
