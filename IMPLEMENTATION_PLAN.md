# Implementation Plan — My Budget AI

Prioritized bullet-point list ordered by dependency. Status: nothing is implemented yet — `src/` is empty, no config files, no tests.

---

## Phase 0: Bootstrap (do first — everything depends on this)

- [ ] Create `.gitignore` — ignore `__pycache__/`, `.venv/`, `data/budget.db`, `.env`, `.DS_Store`, `.ruff_cache/`, `*.egg-info/`
- [ ] Create `pyproject.toml` — name=my-budget-ai, python>=3.11, deps: pandas>=2.0.0, matplotlib>=3.7.0; dev deps: pytest>=7.0.0, ruff>=0.8.0; ruff config: line-length 88, target py311, select E/F/I/W, ignore E501; pytest config: testpaths=tests, pythonpath=["."]
- [ ] Create directory structure with `__init__.py` files: `src/`, `src/models/`, `src/database/`, `src/database/repositories/`, `src/services/`, `src/ui/`, `src/ui/components/`, `src/ui/views/`, `src/utils/`, `data/`, `tests/`, `sample_data/`
- [ ] Create `data/.gitkeep`
- [ ] Create `tests/__init__.py`
- [ ] Create minimal `src/main.py` entry point (prints startup message, exits cleanly)
- [ ] Run `uv venv --python 3.11 && uv pip install -e ".[dev]"` — verify toolchain works
- [ ] Run `ruff check src/` and `pytest` — verify zero errors, zero tests collected
- [ ] Populate `AGENTS.md` with actual build/run/test/lint commands: `uv run pytest -v`, `uv run ruff check src/ tests/`, `uv run python -m src.main`
- [ ] Initial commit

---

## Phase 1: MVP

### 1.1 Data Models (no deps beyond Phase 0)

- [ ] `src/models/account.py` — `Account` dataclass: id, name, type (credit_card/checking/savings), starting_balance, credit_limit (optional), statement_close_day (optional), payment_due_day (optional), created_at, updated_at
- [ ] `src/models/category.py` — `Category` dataclass: id, name, color, keywords: list[str], created_at, updated_at
- [ ] `src/models/transaction.py` — `Transaction` dataclass: id, account_id, type (income/expense/transfer), amount (always positive), description, category_id (optional), date, transfer_to_account_id (optional), notes (optional), created_at, updated_at
- [ ] `src/models/statement.py` — `StatementSnapshot` dataclass: id, account_id, statement_date, balance, due_date, is_paid, created_at, updated_at
- [ ] `src/models/__init__.py` — re-export all 4 model classes

### 1.2 Utilities (no deps beyond Phase 0)

- [ ] `src/utils/date_helpers.py` — `parse_date(str) -> date` (supports YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY, M/D/YYYY), `is_future_date(date) -> bool`
- [ ] `src/utils/formatters.py` — `format_currency(float) -> str` (e.g. "$1,234.56"), `format_signed_currency(float, type) -> str` (prefix +/- based on transaction type)

### 1.3 Database Layer (depends on 1.1 Models)

- [ ] `src/database/connection.py` — singleton connection manager: `get_connection(db_path)`, `close_connection()`, `reset_connection()`; default path `data/budget.db`; enables WAL mode + foreign keys; accepts `:memory:` for tests
- [ ] `src/database/schema.py` — `initialize_database(conn)`: CREATE TABLE IF NOT EXISTS for all 4 tables per `spec/DATA_MODEL.md`; UNIQUE on statement_snapshots(account_id, statement_date); 6 indexes; idempotent
- [ ] `src/database/seeds.py` — `seed_categories(conn)`: INSERT OR IGNORE 8 categories with colors and keyword JSON arrays per spec

### 1.4 Repositories (depends on 1.3 Database Layer)

- [ ] `src/database/repositories/category_repo.py` — `CategoryRepository(conn)`: get_all, get_by_id, get_by_name; parses keywords JSON
- [ ] `src/database/repositories/account_repo.py` — `AccountRepository(conn)`: create, get_by_id, get_all, update, delete
- [ ] `src/database/repositories/transaction_repo.py` — `TransactionRepository(conn)`: create, create_many, get_by_account (with optional date range), get_all (with optional date range), update, delete
- [ ] `src/database/repositories/statement_repo.py` — `StatementRepository(conn)`: create, get_by_account, get_unpaid, mark_paid
- [ ] `src/database/repositories/__init__.py` — re-export all 4 repository classes

### 1.5 Tests: conftest + Repositories (depends on 1.4)

- [ ] `tests/conftest.py` — pytest fixture providing fresh `:memory:` SQLite connection with schema initialized + categories seeded; new connection per test for isolation
- [ ] `tests/test_repositories.py` — CRUD tests for all 4 repos; FK constraint enforcement; date filtering on transactions; keyword JSON round-trip

### 1.6 Services — MVP (depends on 1.4 Repositories + 1.2 Utilities)

- [ ] `src/services/categorizer.py` — `Categorizer(categories: list[Category])`: builds keyword->category map at init; `categorize(description) -> Category | None` (case-insensitive substring match); `categorize_with_fallback(description) -> Category` (returns Uncategorized if no match)
- [ ] `src/services/importer.py` — `CsvImporter`: pandas CSV parsing; type detection (explicit column > income keywords > transfer keywords > expense); amounts stored as abs(); validation (date parseable + not future, amount != 0, description not empty); returns `ImportResult(transactions: list[Transaction], errors: list[str], total_rows: int)`
- [ ] `src/services/balance_calculator.py` — `BalanceCalculator(account_repo, transaction_repo)`: checking/savings = starting_balance + income + transfers_in - expenses - transfers_out; credit_card = starting_balance + expenses - payments_received (transfers IN); `get_balance(account) -> float`, `get_all_balances() -> dict[int, float]`

### 1.7 Tests: Services (depends on 1.6)

- [ ] `tests/test_categorizer.py` — keyword matching, case insensitivity, multi-word keywords, unknown falls back to Uncategorized
- [ ] `tests/test_importer.py` — type detection (income/transfer/expense keywords), amount normalization (negative -> positive), validation rejects future dates / zero amounts / empty descriptions, handles both sign conventions
- [ ] `tests/test_balance_calculator.py` — checking balance calc, CC balance calc (debt model), empty account returns starting_balance, mixed transaction types

### 1.8 Sample Data (no code deps, useful for manual testing)

- [ ] `sample_data/checking_account.csv` — income deposits, CC payment (transfer), expenses; YYYY-MM-DD dates; no type column
- [ ] `sample_data/credit_card.csv` — expenses and payment received; YYYY-MM-DD dates; no type column
- [ ] `sample_data/mixed_format.csv` — explicit type column; MM/DD/YYYY dates; absolute amounts

### 1.9 UI Foundation (depends on 1.1 Models for type refs)

- [ ] `src/ui/theme.py` — CATEGORY_COLORS dict (red=#E53935, orange=#FB8C00, yellow=#FDD835, green=#43A047, blue=#1E88E5, purple=#8E24AA, pink=#D81B60, gray=#757575), FONTS dict (Helvetica family), SPACING constants, WINDOW_SIZE (1100x750)
- [ ] `src/ui/components/data_table.py` — reusable `DataTable` wrapping `ttk.Treeview` with scrollbars, configurable columns, row insertion, clear method
- [ ] `src/ui/components/alert_banner.py` — `AlertBanner` widget: colored banner for warnings/info messages, dismiss capability

### 1.10 UI Views — MVP (depends on 1.9 + 1.6 Services)

- [ ] `src/ui/views/dashboard.py` — `DashboardView`: summary bar (total assets, total liabilities, net worth, current month income/expenses/net); account cards with balances; recent transactions table (last 50)
- [ ] `src/ui/views/accounts.py` — `AccountsView`: list accounts with type/balance; add form (type selector, conditional CC fields: statement_close_day, payment_due_day, credit_limit); edit and delete with confirmation dialog
- [ ] `src/ui/views/import_csv.py` — `ImportCsvView`: file picker -> account selector -> preview first 10 rows with auto-categorization -> confirm/cancel -> import summary with error reporting

### 1.11 Main App Shell (depends on 1.10 Views)

- [ ] `src/ui/app.py` — main Tkinter window: sidebar nav (Dashboard, Accounts, Import CSV), content area with view swapping via `register_views()` + `show_view(name)`, view factory pattern
- [ ] `src/main.py` (full version) — init DB connection, create tables, seed categories, launch Tkinter window, register views, show dashboard, graceful shutdown on close

### 1.12 MVP Verification

- [ ] `pytest -v` — all tests pass
- [ ] `ruff check src/ tests/` — no lint errors
- [ ] `python -m src.main` — app launches, manual smoke test (add account, import CSV, verify dashboard)

---

## Phase 2: Cash Flow, Balance Sheet, Alerts

### 2.1 Services (depends on Phase 1 repos)

- [ ] `src/services/cash_flow.py` — `CashFlowService(transaction_repo, category_repo)`: `get_cash_flow(start_date, end_date, account_id=None) -> CashFlowResult` (total_income, total_expenses, net_cash_flow, expenses_by_category dict); transfers excluded from totals
- [ ] `src/services/balance_sheet.py` — `BalanceSheetService(account_repo, balance_calculator)`: `get_balance_sheet() -> BalanceSheetResult` (assets: dict, liabilities: dict, total_assets, total_liabilities, net_worth)
- [ ] `src/services/alerts.py` — `AlertService(statement_repo)`: `get_due_date_alerts() -> list[Alert]` (unpaid statements due within 7 days); `get_all_alerts() -> list[Alert]`

### 2.2 Tests

- [ ] `tests/test_cash_flow.py` — correct totals, transfers excluded, category breakdown accuracy, date filtering, single-account filtering
- [ ] `tests/test_balance_sheet.py` — net worth = assets - liabilities; correct partitioning by account type; empty state
- [ ] `tests/test_alerts.py` — due within 7 days triggers alert; paid snapshots excluded; outside window excluded; empty state

### 2.3 UI

- [ ] `src/ui/views/reports.py` — `ReportsView` with sub-tabs: Cash Flow (period selector week/month/year, summary, matplotlib bar chart via FigureCanvasTkAgg, category breakdown table); Balance Sheet (assets section, liabilities section, net worth)

### 2.4 Integration Updates

- [ ] Update `src/ui/app.py` — add "Reports" to sidebar nav
- [ ] Update `src/main.py` — register ReportsView
- [ ] Update `src/ui/views/dashboard.py` — display alert banners from AlertService

### 2.5 Phase 2 Verification

- [ ] `pytest -v` — all tests pass (including Phase 2 tests)
- [ ] `ruff check src/ tests/` — no lint errors

---

## Phase 3: Activity Analysis, Transactions View, UI Polish

### 3.1 Services

- [ ] `src/services/reports.py` — `ReportService(transaction_repo, category_repo)`: weekly/monthly/yearly summaries, expenses by category with drill-down transaction lists

### 3.2 Tests

- [ ] `tests/test_reports.py` — monthly/weekly summaries, top category detection, drill-down data accuracy

### 3.3 UI Views

- [ ] `src/ui/views/transactions.py` — `TransactionsView`: search/filter by date range, account, category, amount range; inline category override; notes editing
- [ ] Add Activity Analysis sub-tab to `src/ui/views/reports.py` — period navigation (prev/next), summary card, matplotlib pie chart, category drill-down table

### 3.4 Dashboard Enhancements

- [ ] Add per-account tabs to `src/ui/views/dashboard.py` — `ttk.Notebook`: Tab 0 = all accounts, Tab 1..N = per-account; CC tabs show billing cycle info (statement close day, due date, current balance)

### 3.5 Statement Auto-Calculation

- [ ] `src/services/statement_service.py` (or in main.py) — on startup, check if today >= statement_close_day for each CC; auto-create StatementSnapshot if none exists for current month

### 3.6 UI Polish

- [ ] Category color-coding in transaction tables via Treeview `tag_configure`
- [ ] Amount color-coding: income=green, expenses=red, transfers=neutral gray
- [ ] Alternating row colors + hover states in `src/ui/components/data_table.py`

### 3.7 Integration Updates

- [ ] Update `src/ui/app.py` — add "Transactions" to sidebar nav
- [ ] Update `src/main.py` — register TransactionsView

### 3.8 Phase 3 Verification

- [ ] `pytest -v` — all tests pass
- [ ] `ruff check src/ tests/` — no lint errors

---

## Key Spec References

- **Amounts always positive** — type field determines sign semantics; CSV importer stores `abs(amount)`
- **Dependency injection** — repos/services take `sqlite3.Connection` via constructor; tests use `:memory:` DB
- **Keywords as JSON** — `categories.keywords` is TEXT column storing JSON array, parsed with `json.loads()`
- **View factory pattern** — `app.register_views()` receives callables; views get DB conn without App knowing about database
- **No ORM** — dataclasses + raw SQL; ~4 tables don't warrant ORM complexity
- **Transfer = $0 budget impact** — core differentiator solving CC payment double-counting
- **CATEGORY_COLORS** hex values: red=#E53935, orange=#FB8C00, yellow=#FDD835, green=#43A047, blue=#1E88E5, purple=#8E24AA, pink=#D81B60, gray=#757575
- **CC balance formula**: starting_balance + expenses - payments_received (payments are transfers IN to CC)
- **Checking balance formula**: starting_balance + income + transfers_in - expenses - transfers_out
- **CC fields are conditional** — credit_limit, statement_close_day, payment_due_day only apply to credit_card accounts
- **Date validation** — reject future dates during CSV import
- **Income keywords** (for type detection): DIRECT DEPOSIT, PAYROLL, SALARY, TAX REFUND, INTEREST PAYMENT, DIVIDEND
- **Transfer keywords**: PAYMENT THANK YOU, AUTOPAY, PAYMENT - THANK, ONLINE TRANSFER, TRANSFER TO, TRANSFER FROM
