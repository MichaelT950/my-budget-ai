# Implementation Plan — My Budget AI

Status: All 3 phases complete. 75 tests passing, lint clean. Tags: 0.0.1, 0.0.2, 0.0.3, 0.0.4.

---

## Completed

### Phase 0: Bootstrap
- `.gitignore`, `pyproject.toml`, directory structure, `main.py`, venv setup, `AGENTS.md`

### Phase 1: MVP
- **Models**: `Account`, `Category`, `Transaction`, `StatementSnapshot` dataclasses
- **Utilities**: `date_helpers.py`, `formatters.py`
- **Database**: `connection.py` (singleton, WAL, FK), `schema.py` (4 tables, 6 indexes), `seeds.py` (8 categories)
- **Repositories**: CRUD for all 4 entities
- **Services**: `Categorizer`, `CsvImporter`, `BalanceCalculator`
- **UI Foundation**: `theme.py`, `DataTable`, `AlertBanner`
- **UI Views**: `DashboardView`, `AccountsView`, `ImportCsvView`
- **App Shell**: sidebar nav, content area, view factory pattern
- **Sample Data**: 3 CSV files
- **Tests**: 55 tests (repos + services)

### Phase 2: Cash Flow, Balance Sheet, Alerts
- **Services**: `CashFlowService`, `BalanceSheetService`, `AlertService`
- **UI**: `ReportsView` (Cash Flow + Balance Sheet tabs, matplotlib charts)
- **Integration**: Alert banners on Dashboard, Reports in sidebar
- **Tests**: 15 new tests (cash flow, balance sheet, alerts)

### Phase 3: Activity Analysis, Transactions, UI Polish
- **Services**: `ReportService` (weekly/monthly/yearly summaries, category drill-down), `StatementService` (auto-create snapshots)
- **UI**: `TransactionsView` (search, filter, inline category/notes edit)
- **UI Polish**: Alternating row colors in DataTable
- **Integration**: Transactions in sidebar, statement auto-calc on startup
- **Tests**: 5 new tests (report service)

---

## Key Spec References

- **Amounts always positive** — type field determines sign semantics; CSV importer stores `abs(amount)`
- **Dependency injection** — repos/services take `sqlite3.Connection` via constructor; tests use `:memory:` DB
- **Keywords as JSON** — `categories.keywords` is TEXT column storing JSON array, parsed with `json.loads()`
- **Transfer = $0 budget impact** — core differentiator solving CC payment double-counting
- **CC balance formula**: starting_balance + expenses - payments_received (payments are transfers IN to CC)
- **Checking balance formula**: starting_balance + income + transfers_in - expenses - transfers_out

## Learnings

- `uv` on this system is installed as a Python package — use `python3 -m uv` (not bare `uv`)
- venv Python is 3.11.5 at `.venv/bin/python`, system Python is 3.9.6
- Install command: `python3 -m uv pip install -e ".[dev]" --python .venv/bin/python`
