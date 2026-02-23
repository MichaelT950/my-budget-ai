// TypeScript interfaces matching backend Pydantic schemas

// --- Accounts ---

export interface Account {
  id: number;
  name: string;
  type: 'credit_card' | 'checking' | 'savings';
  starting_balance: number;
  credit_limit: number | null;
  statement_close_day: number | null;
  payment_due_day: number | null;
  balance: number | null;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  type: 'credit_card' | 'checking' | 'savings';
  starting_balance?: number;
  credit_limit?: number | null;
  statement_close_day?: number | null;
  payment_due_day?: number | null;
}

export interface AccountUpdate {
  name: string;
  type: 'credit_card' | 'checking' | 'savings';
  starting_balance?: number;
  credit_limit?: number | null;
  statement_close_day?: number | null;
  payment_due_day?: number | null;
}

// --- Transactions ---

export interface Transaction {
  id: number;
  account_id: number;
  type: 'income' | 'expense' | 'transfer';
  amount: number;
  description: string;
  category_id: number | null;
  date: string;
  transfer_to_account_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: number;
  type: 'income' | 'expense' | 'transfer';
  amount: number;
  description: string;
  category_id?: number | null;
  date: string;
  transfer_to_account_id?: number | null;
  notes?: string | null;
}

export interface TransactionUpdate {
  account_id?: number;
  type?: string;
  amount?: number;
  description?: string;
  category_id?: number | null;
  date?: string;
  transfer_to_account_id?: number | null;
  notes?: string | null;
}

// --- Categories ---

export interface Category {
  id: number;
  name: string;
  color: string;
  keywords: string[];
}

// --- Statements ---

export interface Statement {
  id: number;
  account_id: number;
  statement_date: string;
  balance: number;
  due_date: string;
  is_paid: boolean;
  created_at: string;
  updated_at: string;
}

// --- Import ---

export interface ImportPreviewTransaction {
  account_id: number;
  type: string;
  amount: number;
  description: string;
  date: string;
}

export interface ImportPreviewResponse {
  transactions: ImportPreviewTransaction[];
  errors: string[];
  total_rows: number;
}

export interface ImportConfirmRequest {
  account_id: number;
  transactions: ImportPreviewTransaction[];
}

export interface ImportConfirmResponse {
  imported_count: number;
}

// --- Reports ---

export interface CashFlowResponse {
  total_income: number;
  total_expenses: number;
  net_cash_flow: number;
  expenses_by_category: Record<string, number>;
}

export interface BalanceSheetResponse {
  assets: Record<string, number>;
  liabilities: Record<string, number>;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
}

export interface CategorySummary {
  name: string;
  total: number;
  count: number;
}

export interface PeriodSummaryResponse {
  period_label: string;
  start_date: string;
  end_date: string;
  total_income: number;
  total_expenses: number;
  net: number;
  top_category: string;
  expenses_by_category: CategorySummary[];
}

// --- Dashboard ---

export interface Alert {
  message: string;
  alert_type: string;
  account_name: string;
  due_date: string;
  balance: number;
}

export interface DashboardResponse {
  accounts: Account[];
  alerts: Alert[];
  cash_flow: CashFlowResponse;
  balance_sheet: BalanceSheetResponse;
}
