# Implementation Plan — My Budget AI

Status: Phase 0 + Phase 1 (1.1–1.8) complete. 55 tests passing, lint clean.

---

## Completed

- **Phase 0: Bootstrap** — `.gitignore`, `pyproject.toml`, directory structure, `main.py`, venv setup, `AGENTS.md`
- **Phase 1.1: Data Models** — `Account`, `Category`, `Transaction`, `StatementSnapshot` dataclasses
- **Phase 1.2: Utilities** — `date_helpers.py` (parse_date, is_future_date), `formatters.py` (format_currency, format_signed_currency)
- **Phase 1.3: Database Layer** — `connection.py` (singleton, WAL, FK), `schema.py` (4 tables, 6 indexes), `seeds.py` (8 categories)
- **Phase 1.4: Repositories** — `CategoryRepository`, `AccountRepository`, `TransactionRepository`, `StatementRepository`
- **Phase 1.5: Tests (repos)** — `conftest.py` (:memory: fixture), `test_repositories.py` (CRUD, FK, date filter, JSON round-trip)
- **Phase 1.6: Services** — `Categorizer` (keyword matching), `CsvImporter` (pandas, type detection, validation), `BalanceCalculator` (checking/CC formulas)
- **Phase 1.7: Tests (services)** — `test_categorizer.py`, `test_importer.py`, `test_balance_calculator.py`
- **Phase 1.8: Sample Data** — `checking_account.csv`, `credit_card.csv`, `mixed_format.csv`

---

## Next Up: Phase 1.9–1.12 (UI + App Shell)

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

## Learnings

- `uv` on this system is installed as a Python package — use `python3 -m uv` (not bare `uv`)
- venv Python is 3.11.5 at `.venv/bin/python`, system Python is 3.9.6
- Install command: `python3 -m uv pip install -e ".[dev]" --python .venv/bin/python`
