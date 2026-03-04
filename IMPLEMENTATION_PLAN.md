# Implementation Plan — My Budget AI

Status: 132 backend tests passing, frontend builds clean. Tags: 0.0.1–0.0.7.

---

## Completed

### Phase 0–3: Original MVP (tag 0.0.4)
- Models, database, repositories, services, utils — all business logic
- 75 tests covering repos + services
- CustomTkinter desktop GUI (now deleted)

### Phase 4: Backend Migration (tag 0.0.5)
- Moved all business logic into `backend/` monorepo half
- **FastAPI API layer** (`backend/src/api/`): app.py, deps.py, schemas.py, 7 routers
- **18 REST endpoints**: accounts CRUD, transactions CRUD+filters, categories, statements, dashboard, reports (cash-flow, balance-sheet, period-summary), CSV import (preview+confirm)
- **importer.py** updated to accept file-like objects for multipart upload
- **pyproject.toml** swapped GUI deps (customtkinter, matplotlib) for FastAPI stack (fastapi, uvicorn, python-multipart, httpx)
- **API integration tests**: 18 new tests in `backend/tests/test_api/test_endpoints.py`
- Deleted old `src/ui/`, `src/main.py`, top-level `src/` (canonical code now in `backend/src/`)

### Phase 5: Frontend (tag 0.0.5)
- **React + TypeScript + Vite** scaffold with Tailwind CSS, TanStack Query, React Router, Recharts
- **Types** (`frontend/src/types/index.ts`): TS interfaces matching all Pydantic schemas
- **API layer** (`frontend/src/api/`): typed fetch wrappers — client.ts, accounts.ts, transactions.ts, categories.ts, reports.ts, import.ts, dashboard.ts
- **Components**: Layout (sidebar+outlet), Sidebar (5 nav items), DataTable (generic, alternating rows), AlertBanner
- **Pages**:
  - Dashboard: balance sheet cards, cash flow bar chart, category pie chart, accounts table, alerts
  - Accounts: CRUD with inline form, credit card fields conditional
  - Transactions: search, account filter, inline category edit, inline notes, delete
  - Import CSV: 3-step flow (select file+account → preview → confirm)
  - Reports: 3 tabs (Cash Flow with charts, Balance Sheet, Period Summary with category breakdown)
- **Utils**: formatters.ts (currency, date, account type, transaction type, category colors)
- Frontend builds cleanly (`tsc -b && vite build`)

### Phase 6: Alerts, Bug Fixes, Test Coverage, Production Script (tag 0.0.6)
- **Overdraft alerts**: `AlertService.get_overdraft_alerts()` — warns when checking/savings balance goes negative. Wired to `BalanceCalculator` for real-time balance checks.
- **Expense threshold alerts**: `AlertService.get_expense_threshold_alerts()` — warns when current-month expenses reach 90%+ of income (warning) or exceed 100% (error). Uses `CashFlowService`.
- **AlertService constructor** now takes 4 deps: `statement_repo`, `account_repo`, `balance_calculator`, `cash_flow_service`. DI container and dashboard router updated accordingly.
- **Date parsing bug fix**: `parse_date()` now handles `M/D/YYYY` (unpadded single-digit month/day) by parsing numeric components directly instead of relying solely on `strptime` format strings.
- **StatementService tests** (7 tests): snapshot creation on close day, skip non-CC accounts, skip before close day, idempotency, due date next month when due_day < close_day, December→January rollover, skip accounts without close_day.
- **Statements API tests** (4 tests): list by account, list unpaid, mark paid, mark nonexistent 404.
- **New alert tests** (8 tests): overdraft trigger/no-trigger/CC-excluded, expense threshold at 90%/100%+/below 90%/zero income, get_all_alerts combines all types.
- **Importer test**: `M/D/YYYY` unpadded date format parsing.
- **start.sh**: Production script that builds frontend and serves full app via uvicorn on port 8000.
- Total: 113 tests passing (was 93)

### Phase 7: Transaction Creation, Statements UI, Test Coverage (tag 0.0.7)
- **Bug fix**: `auto_create_statements()` was never called at startup — wired into `app.py` lifespan so CC statement snapshots are created when the app boots.
- **Manual transaction creation**: Transactions page now has an "Add Transaction" form with conditional fields (category for expenses, transfer-to for transfers). Auto-categorizes expenses server-side.
- **Date filtering on Transactions**: Start/end date inputs in the filter bar, wired to backend query params.
- **Statements page**: New frontend page (`/statements`) showing CC statement snapshots with All/Unpaid toggle, account filter, overdue highlighting (red), and "Mark Paid" button. API client `statements.ts` added.
- **Sidebar updated**: 6 nav items (added Statements after Reports).
- **Test coverage** (19 new tests):
  - `test_date_helpers.py` (8 tests): `parse_date` for ISO/slash/unpadded/dash formats + invalid input; `is_future_date` boundary tests.
  - `test_formatters.py` (6 tests): `format_currency` basic/zero/negative; `format_signed_currency` for income/expense/transfer.
  - API 404 tests (5 tests): PUT/DELETE nonexistent account/transaction return 404; dashboard with populated data.
- Total: 132 tests passing (was 113)

---

## Key Spec References

- **Amounts always positive** — type field determines sign semantics; CSV importer stores `abs(amount)`
- **Dependency injection** — repos/services take `sqlite3.Connection` via constructor; tests use `:memory:` DB
- **Keywords as JSON** — `categories.keywords` is TEXT column storing JSON array, parsed with `json.loads()`
- **Transfer = $0 budget impact** — core differentiator solving CC payment double-counting
- **CC balance formula**: starting_balance + expenses - payments_received (payments are transfers IN to CC)
- **Checking balance formula**: starting_balance + income + transfers_in - expenses - transfers_out
- **Three alert types**: payment due dates (7-day window), overdraft on checking/savings, expenses approaching income (90% threshold)

## Learnings

- `uv` on this system is installed as a Python package — use `python3 -m uv` (not bare `uv`)
- venv Python is 3.11.5 at `.venv/bin/python`, system Python is 3.9.6
- Install command: `python3 -m uv pip install -e ".[dev]" --python .venv/bin/python`
- System Node.js is v18.13.0 (too old for Vite 7); use `/usr/local/Cellar/node/25.2.1/bin/node` for frontend builds
- Frontend npm install requires `PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH"` to avoid spawn sh ENOENT
- Recharts v3 formatter callbacks accept `number | string | undefined` — don't type-annotate the param, use `Number(v ?? 0)`
- TypeScript `erasableSyntaxOnly` forbids parameter properties (`public x: T` in constructors); use explicit field declaration
- `date.fromisoformat()` works for mock patching; `unittest.mock.patch` with `side_effect = lambda *a, **kw: date(*a, **kw)` preserves `date()` constructor while mocking `date.today()`

## Future Work

- **CSV Column Mapping UI** (post-MVP)
- **Duplicate Detection** on import (post-MVP)
- **Split Transactions** — `split_group_id` column (post-MVP)
