"""Pydantic request/response schemas for the API."""

from pydantic import BaseModel


# --- Accounts ---

class AccountCreate(BaseModel):
    name: str
    type: str  # credit_card, checking, savings
    starting_balance: float = 0.0
    credit_limit: float | None = None
    statement_close_day: int | None = None
    payment_due_day: int | None = None


class AccountUpdate(BaseModel):
    name: str
    type: str
    starting_balance: float = 0.0
    credit_limit: float | None = None
    statement_close_day: int | None = None
    payment_due_day: int | None = None


class AccountResponse(BaseModel):
    id: int
    name: str
    type: str
    starting_balance: float
    credit_limit: float | None
    statement_close_day: int | None
    payment_due_day: int | None
    balance: float | None = None
    created_at: str
    updated_at: str


# --- Transactions ---

class TransactionCreate(BaseModel):
    account_id: int
    type: str  # income, expense, transfer
    amount: float
    description: str
    category_id: int | None = None
    date: str
    transfer_to_account_id: int | None = None
    notes: str | None = None


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    type: str | None = None
    amount: float | None = None
    description: str | None = None
    category_id: int | None = None
    date: str | None = None
    transfer_to_account_id: int | None = None
    notes: str | None = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    type: str
    amount: float
    description: str
    category_id: int | None
    date: str
    transfer_to_account_id: int | None
    notes: str | None
    created_at: str
    updated_at: str


# --- Categories ---

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    keywords: list[str]


# --- Statements ---

class StatementResponse(BaseModel):
    id: int
    account_id: int
    statement_date: str
    balance: float
    due_date: str
    is_paid: bool
    created_at: str
    updated_at: str


# --- Import ---

class ImportPreviewTransaction(BaseModel):
    account_id: int
    type: str
    amount: float
    description: str
    date: str
    category_id: int | None = None
    is_duplicate: bool = False


class ImportPreviewResponse(BaseModel):
    transactions: list[ImportPreviewTransaction]
    errors: list[str]
    total_rows: int
    duplicate_count: int = 0


class ImportConfirmRequest(BaseModel):
    account_id: int
    transactions: list[ImportPreviewTransaction]


class ImportConfirmResponse(BaseModel):
    imported_count: int
    skipped_duplicates: int = 0


# --- Reports ---

class CashFlowResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    expenses_by_category: dict[str, float]


class BalanceSheetResponse(BaseModel):
    assets: dict[str, float]
    liabilities: dict[str, float]
    total_assets: float
    total_liabilities: float
    net_worth: float


class CategorySummaryResponse(BaseModel):
    name: str
    total: float
    count: int


class PeriodSummaryResponse(BaseModel):
    period_label: str
    start_date: str
    end_date: str
    total_income: float
    total_expenses: float
    net: float
    top_category: str
    expenses_by_category: list[CategorySummaryResponse]


# --- Dashboard ---

class AlertResponse(BaseModel):
    message: str
    alert_type: str
    account_name: str
    due_date: str
    balance: float


class DashboardResponse(BaseModel):
    accounts: list[AccountResponse]
    alerts: list[AlertResponse]
    cash_flow: CashFlowResponse
    balance_sheet: BalanceSheetResponse
