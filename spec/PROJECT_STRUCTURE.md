# Project Structure

## Directory Layout (Monorepo)

```
my-budget-ai/
├── spec/                          # Specification documents
│   ├── README.md                  # Main specification
│   ├── DATA_MODEL.md              # Database schema and queries
│   ├── PROJECT_STRUCTURE.md       # This file
│   ├── CSV_SCHEMA.md              # CSV import format
│   └── MIGRATION.md               # React+FastAPI migration plan
│
├── backend/                       # Python backend (FastAPI)
│   ├── pyproject.toml             # Python dependencies and config
│   ├── run.py                     # Uvicorn entry point
│   │
│   ├── src/                       # Application source code
│   │   ├── __init__.py
│   │   │
│   │   ├── models/                # Data models (dataclasses)
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   └── statement.py
│   │   │
│   │   ├── database/              # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py      # SQLite connection factory
│   │   │   ├── schema.py          # Table creation and migrations
│   │   │   ├── seeds.py           # Seed data (categories)
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── account_repo.py
│   │   │       ├── transaction_repo.py
│   │   │       ├── category_repo.py
│   │   │       └── statement_repo.py
│   │   │
│   │   ├── services/              # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── categorizer.py
│   │   │   ├── importer.py        # CSV import (accepts path or file-like)
│   │   │   ├── balance_calculator.py
│   │   │   ├── cash_flow.py
│   │   │   ├── balance_sheet.py
│   │   │   ├── alerts.py
│   │   │   ├── reports.py
│   │   │   └── statement_service.py
│   │   │
│   │   ├── api/                   # FastAPI REST API
│   │   │   ├── __init__.py
│   │   │   ├── app.py             # FastAPI app, lifespan, CORS
│   │   │   ├── deps.py            # Dependency injection
│   │   │   ├── schemas.py         # Pydantic request/response models
│   │   │   └── routers/
│   │   │       ├── __init__.py
│   │   │       ├── accounts.py
│   │   │       ├── transactions.py
│   │   │       ├── categories.py
│   │   │       ├── statements.py
│   │   │       ├── dashboard.py
│   │   │       ├── reports.py
│   │   │       └── import_csv.py
│   │   │
│   │   └── utils/                 # Utility functions
│   │       ├── __init__.py
│   │       ├── date_helpers.py
│   │       └── formatters.py
│   │
│   ├── data/                      # Data directory
│   │   ├── .gitkeep
│   │   └── budget.db              # SQLite database (created at runtime)
│   │
│   ├── tests/                     # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py            # pytest fixtures
│   │   ├── test_categorizer.py
│   │   ├── test_importer.py
│   │   ├── test_balance_calculator.py
│   │   ├── test_balance_sheet.py
│   │   ├── test_cash_flow.py
│   │   ├── test_alerts.py
│   │   ├── test_reports.py
│   │   ├── test_repositories.py
│   │   └── test_api/              # API integration tests
│   │       ├── __init__.py
│   │       └── test_endpoints.py
│   │
│   └── sample_data/               # Sample CSV files
│       ├── checking_account.csv
│       ├── credit_card.csv
│       └── mixed_format.csv
│
├── frontend/                      # React + TypeScript frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx               # React entry point
│       ├── App.tsx                # Routes and providers
│       ├── index.css              # Tailwind imports
│       │
│       ├── api/                   # Typed API client
│       │   ├── client.ts          # Base fetch wrapper
│       │   ├── accounts.ts
│       │   ├── transactions.ts
│       │   ├── categories.ts
│       │   ├── reports.ts
│       │   ├── import.ts
│       │   └── dashboard.ts
│       │
│       ├── types/
│       │   └── index.ts           # TS interfaces matching Pydantic schemas
│       │
│       ├── components/
│       │   ├── Layout.tsx         # Sidebar + Outlet
│       │   ├── Sidebar.tsx
│       │   ├── DataTable.tsx
│       │   └── AlertBanner.tsx
│       │
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Accounts.tsx
│       │   ├── Transactions.tsx
│       │   ├── ImportCsv.tsx
│       │   └── Reports.tsx
│       │
│       └── utils/
│           └── formatters.ts      # Currency formatting helpers
│
└── .gitignore
```

---

## Architecture

```
React (Frontend) → FastAPI REST API (Backend) → Services → Repositories → SQLite
```

Each layer only depends on the layer below it.

### Backend Layers

- **API Layer** (`src/api/`): FastAPI routers, Pydantic schemas, dependency injection
- **Services** (`src/services/`): Business logic, independent of API and database implementation
- **Repositories** (`src/database/repositories/`): CRUD operations returning model objects
- **Models** (`src/models/`): Python dataclasses representing domain entities

### Frontend Layers

- **Pages** (`src/pages/`): Full-page views mapped to routes
- **Components** (`src/components/`): Reusable UI components
- **API Client** (`src/api/`): Typed fetch wrappers per resource
- **Types** (`src/types/`): TypeScript interfaces matching backend schemas

---

## Key Design Decisions

### 1. Monorepo Structure
Backend and frontend live in the same repository for easy development and deployment.

### 2. Repository Pattern
Database operations are encapsulated in repository classes, returning model objects.

### 3. Dependency Injection
FastAPI's `Depends()` chain provides connections, repos, and services to route handlers.

### 4. Single Database File
All data in `backend/data/budget.db`. Easy backup (copy the file).

### 5. TanStack Query for State
Server state managed via React Query — automatic caching, refetching, and invalidation.

---

## Running the Application

```bash
# Backend
cd backend
python -m uv pip install -e ".[dev]" --python .venv/bin/python
.venv/bin/python run.py              # Starts on http://localhost:8000
.venv/bin/pytest -v                  # Run tests

# Frontend
cd frontend
npm install
npm run dev                          # Starts on http://localhost:5173 (proxies /api to backend)

# Production
./start.sh                           # Builds frontend + starts uvicorn serving everything
```
