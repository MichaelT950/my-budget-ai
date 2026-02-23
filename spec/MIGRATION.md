# Migration Plan: React + FastAPI

## Context

My Budget AI is a personal budgeting desktop app built with CustomTkinter (Python GUI), SQLite, and a clean service/repository architecture (75 tests passing, tag 0.0.4). The goal is to replace the desktop GUI with a **React + TypeScript frontend** and expose the backend via **FastAPI**, turning it into a local web app while preserving all existing business logic and tests.

---

## Tech Stack

| Layer | Current | New |
|-------|---------|-----|
| Frontend | CustomTkinter (Python) | React + TypeScript + Vite |
| Styling | Tkinter theme.py | Tailwind CSS |
| Charts | matplotlib | Recharts |
| State mgmt | Tkinter refresh() | TanStack Query (React Query) |
| Routing | Sidebar view swap | React Router v6 |
| Backend | Direct Python calls | FastAPI REST API |
| Database | SQLite | SQLite (unchanged) |

---

## Project Structure (Monorepo)

```
my-budget-ai/
  backend/
    pyproject.toml
    run.py                          # uvicorn entry point
    src/
      database/                     # UNCHANGED (connection, schema, seeds, repositories)
      models/                       # UNCHANGED (dataclasses)
      services/                     # UNCHANGED (except importer.py minor tweak)
      utils/                        # UNCHANGED
      api/                          # NEW
        app.py                      # FastAPI app, lifespan, CORS, router mount
        deps.py                     # DI: get_conn, get_repos, get_services
        schemas.py                  # Pydantic request/response models
        routers/
          accounts.py
          transactions.py
          categories.py
          statements.py
          dashboard.py
          reports.py
          import_csv.py
    tests/                          # Existing tests + new API tests
      conftest.py                   # UNCHANGED
      test_*.py                     # UNCHANGED (all 75 pass)
      test_api/                     # NEW: API integration tests

  frontend/
    package.json
    tsconfig.json
    vite.config.ts
    tailwind.config.ts
    index.html
    src/
      main.tsx
      App.tsx
      api/                          # Typed fetch wrappers per resource
        client.ts
        accounts.ts
        transactions.ts
        categories.ts
        reports.ts
        import.ts
        dashboard.ts
      types/
        index.ts                    # TS interfaces matching Pydantic schemas
      components/
        Layout.tsx                  # Sidebar + Outlet
        Sidebar.tsx
        DataTable.tsx
        AlertBanner.tsx
      pages/
        Dashboard.tsx
        Accounts.tsx
        Transactions.tsx
        ImportCsv.tsx
        Reports.tsx
      utils/
        formatters.ts               # Port of format_currency etc.
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/accounts` | List all accounts with computed balances |
| POST | `/api/accounts` | Create account |
| GET | `/api/accounts/{id}` | Get single account |
| PUT | `/api/accounts/{id}` | Update account |
| DELETE | `/api/accounts/{id}` | Delete account |
| GET | `/api/transactions?start_date=&end_date=&account_id=&category_id=` | List with filters |
| POST | `/api/transactions` | Create transaction |
| PUT | `/api/transactions/{id}` | Update (category, notes) |
| DELETE | `/api/transactions/{id}` | Delete transaction |
| GET | `/api/categories` | List all categories |
| GET | `/api/statements?account_id=` | List statements |
| GET | `/api/statements/unpaid` | Unpaid statements |
| PATCH | `/api/statements/{id}/paid` | Mark paid |
| POST | `/api/import/preview` | Upload CSV (multipart), return preview |
| POST | `/api/import/confirm` | Confirm import (send transactions array) |
| GET | `/api/reports/cash-flow?start_date=&end_date=&account_id=` | Cash flow report |
| GET | `/api/reports/balance-sheet` | Balance sheet |
| GET | `/api/reports/period-summary?start_date=&end_date=` | Period summary |
| GET | `/api/dashboard` | All dashboard data in one call |

---

## Key Files Modified

| File | Change |
|------|--------|
| `src/database/connection.py` | Remove singleton global, keep factory |
| `src/services/importer.py` | Accept file-like object in addition to path |
| `pyproject.toml` | Swap GUI deps for FastAPI deps |

## Files Deleted
- Entire `src/ui/` package (app.py, theme.py, components/, views/)
- `main.py` (Tkinter entry point)

## Files Unchanged (all 75 tests keep passing)
- All repositories (4 files)
- All models (4 files)
- All services except importer (7 files)
- All utils (2 files)
- All existing tests (9 files)
- `schema.py`, `seeds.py`
