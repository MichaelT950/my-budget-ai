# Data Model

## Overview

SQLite database with four primary tables: accounts, transactions, categories, and statement_snapshots.

---

## Entity Relationship Diagram (Text)

```
┌─────────────────┐       ┌─────────────────────┐
│    accounts     │       │     categories      │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │       │ id (PK)             │
│ name            │       │ name                │
│ type            │       │ color               │
│ starting_balance│       │ keywords (JSON)     │
│ credit_limit    │       └─────────────────────┘
│ statement_close │               │
│ payment_due_day │               │
│ created_at      │               │
│ updated_at      │               │
└─────────────────┘               │
        │                         │
        │ 1:N                     │ 1:N
        ▼                         ▼
┌───────────────────────────────────────────┐
│              transactions                  │
├───────────────────────────────────────────┤
│ id (PK)                                   │
│ account_id (FK → accounts)                │
│ type (income/expense/transfer)            │
│ amount                                    │
│ description                               │
│ category_id (FK → categories, nullable)   │
│ date                                      │
│ transfer_to_account_id (FK, nullable)     │
│ notes                                     │
│ created_at                                │
│ updated_at                                │
└───────────────────────────────────────────┘

┌─────────────────────────────────┐
│      statement_snapshots        │
├─────────────────────────────────┤
│ id (PK)                         │
│ account_id (FK → accounts)      │
│ statement_date                  │
│ balance                         │
│ due_date                        │
│ is_paid                         │
│ created_at                      │
│ updated_at                      │
└─────────────────────────────────┘
```

---

## Tables

### accounts

Stores all financial accounts (credit cards, checking, savings).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL, UNIQUE | Account name (e.g., "Chase Sapphire") |
| type | TEXT | NOT NULL, CHECK(type IN ('credit_card', 'checking', 'savings')) | Account type |
| starting_balance | REAL | NOT NULL, DEFAULT 0 | Initial balance (positive for assets, positive for CC debt) |
| credit_limit | REAL | NULL | Only for credit cards |
| statement_close_day | INTEGER | NULL, CHECK(1-31) | Day of month statement closes (CC only) |
| payment_due_day | INTEGER | NULL, CHECK(1-31) | Day of month payment due (CC only) |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Notes:**
- For credit cards: `starting_balance` represents initial debt (positive number = money owed)
- For checking/savings: `starting_balance` represents initial balance (positive number = money available)

---

### categories

Predefined expense categories with color coding and keyword rules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL, UNIQUE | Category name |
| color | TEXT | NOT NULL | Color code (red, orange, yellow, green, blue, purple, pink, gray) |
| keywords | TEXT | NOT NULL, DEFAULT '[]' | JSON array of keywords for auto-categorization |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Seed Data:**

| name | color | keywords |
|------|-------|----------|
| Health | red | ["doctor", "pharmacy", "medical", "hospital", "clinic", "dental", "vision", "health"] |
| Food & Drink | orange | ["grocery", "restaurant", "uber eats", "doordash", "grubhub", "starbucks", "coffee", "food"] |
| Shopping | yellow | ["amazon", "target", "walmart", "clothing", "electronics", "store", "shop", "retail"] |
| Travel | green | ["airline", "hotel", "airbnb", "booking", "flight", "vacation", "travel", "trip"] |
| Transportation | blue | ["gas", "uber", "lyft", "parking", "transit", "metro", "fuel", "car", "auto"] |
| Services | purple | ["utility", "subscription", "netflix", "spotify", "electric", "water", "internet", "phone"] |
| Entertainment | pink | ["movie", "theater", "concert", "gaming", "steam", "playstation", "xbox", "hulu"] |
| Uncategorized | gray | [] |

---

### transactions

All financial transactions across all accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| account_id | INTEGER | NOT NULL, FK → accounts(id) | Source account |
| type | TEXT | NOT NULL, CHECK(type IN ('income', 'expense', 'transfer')) | Transaction type |
| amount | REAL | NOT NULL, CHECK(amount > 0) | Always positive; sign determined by type |
| description | TEXT | NOT NULL | Transaction description from bank/user |
| category_id | INTEGER | NULL, FK → categories(id) | Only for expenses |
| date | TEXT | NOT NULL | Transaction date (YYYY-MM-DD) |
| transfer_to_account_id | INTEGER | NULL, FK → accounts(id) | Destination account (transfers only) |
| notes | TEXT | NULL | User-added notes |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Transaction Type Rules:**

| Type | account_id effect | transfer_to_account_id | category_id | Budget Impact |
|------|-------------------|------------------------|-------------|---------------|
| income | Balance increases | NULL | NULL | +amount |
| expense | Balance decreases (or debt increases for CC) | NULL | Required | -amount |
| transfer | Balance decreases | Required (balance increases) | NULL | $0 |

---

### statement_snapshots

Monthly credit card statement records for tracking statement vs. current balance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| account_id | INTEGER | NOT NULL, FK → accounts(id) | Credit card account |
| statement_date | TEXT | NOT NULL | Statement close date (YYYY-MM-DD) |
| balance | REAL | NOT NULL | Statement balance (auto-calculated, editable) |
| due_date | TEXT | NOT NULL | Payment due date (YYYY-MM-DD) |
| is_paid | INTEGER | NOT NULL, DEFAULT 0 | Boolean: 1 if paid, 0 if not |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Unique Constraint:** (account_id, statement_date)

---

## Calculated Fields (Not Stored)

These are computed at query time, not stored in the database:

### Account Balance

**For Checking/Savings:**
```sql
starting_balance
+ SUM(income transactions)
- SUM(expense transactions)
- SUM(transfers out)
+ SUM(transfers in)
```

**For Credit Cards:**
```sql
starting_balance
+ SUM(expense transactions)  -- increases debt
- SUM(transfers in)          -- payments reduce debt
```

### Net Worth (Balance Sheet)
```sql
SUM(checking balances) + SUM(savings balances) - SUM(credit card balances)
```

### Cash Flow (Period)
```sql
SUM(income in period) - SUM(expenses in period)
-- Transfers excluded
```

---

## Indexes

```sql
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_statement_snapshots_account_id ON statement_snapshots(account_id);
CREATE INDEX idx_statement_snapshots_due_date ON statement_snapshots(due_date);
```

---

## Sample Queries

### Get account balance (checking/savings)
```sql
SELECT
    a.starting_balance +
    COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN t.type = 'transfer' AND t.account_id = a.id THEN t.amount ELSE 0 END), 0) +
    COALESCE(SUM(CASE WHEN t.type = 'transfer' AND t.transfer_to_account_id = a.id THEN t.amount ELSE 0 END), 0)
    AS current_balance
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id OR t.transfer_to_account_id = a.id
WHERE a.id = ?
GROUP BY a.id;
```

### Get credit card balance (debt)
```sql
SELECT
    a.starting_balance +
    COALESCE(SUM(CASE WHEN t.type = 'expense' AND t.account_id = a.id THEN t.amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN t.type = 'transfer' AND t.transfer_to_account_id = a.id THEN t.amount ELSE 0 END), 0)
    AS current_balance
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id OR t.transfer_to_account_id = a.id
WHERE a.id = ? AND a.type = 'credit_card'
GROUP BY a.id;
```

### Get upcoming due dates (next 7 days)
```sql
SELECT
    a.name,
    ss.balance,
    ss.due_date,
    julianday(ss.due_date) - julianday('now') AS days_until_due
FROM statement_snapshots ss
JOIN accounts a ON a.id = ss.account_id
WHERE ss.is_paid = 0
  AND ss.due_date >= date('now')
  AND ss.due_date <= date('now', '+7 days')
ORDER BY ss.due_date;
```

### Cash flow for current month
```sql
SELECT
    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expenses,
    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS net_cash_flow
FROM transactions
WHERE date >= date('now', 'start of month')
  AND date < date('now', 'start of month', '+1 month');
```

### Expenses by category for current month
```sql
SELECT
    c.name,
    c.color,
    SUM(t.amount) AS total,
    COUNT(*) AS transaction_count
FROM transactions t
JOIN categories c ON c.id = t.category_id
WHERE t.type = 'expense'
  AND t.date >= date('now', 'start of month')
  AND t.date < date('now', 'start of month', '+1 month')
GROUP BY c.id
ORDER BY total DESC;
```

---

## Split Transactions (Future)

For MVP, split transactions can be handled by creating multiple transaction records with the same date/description but different categories and partial amounts.

Future iteration could add a `split_group_id` column to link related splits:

```sql
ALTER TABLE transactions ADD COLUMN split_group_id TEXT NULL;
```
