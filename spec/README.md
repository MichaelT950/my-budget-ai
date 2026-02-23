# My Budget AI

## Summary

A personal local web app for tracking expenses across multiple credit cards and bank accounts, comparing them against income, with AI-powered categorization. The core differentiator is **correct handling of credit card payments** - avoiding the double-counting problem found in traditional budgeting apps.

## App Name
"My Budget AI"

## Purpose
Personal offline tool to:
- Track expenses across 5 credit cards + checking/savings accounts
- Compare expenses against incoming income
- Use AI-powered automated categorization for analysis
- Monitor net financial position (Balance Sheet + Cash Flow views)
- Track credit card billing cycles and payment due dates

## Target User
Single user, no multi-user features.

## Core Value Proposition
- **No double-counting**: Credit card purchases are expenses; payments are transfers
- Aggregate manual transaction data from all accounts
- Auto-categorize expenses with color-coding
- Track expenses vs. income with both Balance Sheet and Cash Flow views
- Simple aggregates for weekly/monthly/yearly insights
- Billing cycle awareness with 7-day advance due date warnings
- Runs locally — all data stays on your machine

---

## Key Functional Requirements

### 1. Account Management

**Account Types:**
- Credit Cards (track as debt/liability)
- Checking Accounts (track as asset)
- Savings Accounts (track as asset)

**Credit Card Setup:**
| Field | Required | Description |
|-------|----------|-------------|
| Name | Yes | e.g., "Chase Sapphire" |
| Statement Close Day | Yes | Day of month (1-31) |
| Payment Due Day | Yes | Day of month (1-31) |
| Starting Balance | Yes | Current debt amount |
| Credit Limit | No | For utilization tracking |

**Checking/Savings Setup:**
| Field | Required | Description |
|-------|----------|-------------|
| Name | Yes | e.g., "Chase Checking" |
| Starting Balance | Yes | Current balance |

**Operations:**
- Add accounts dynamically
- Remove accounts (with confirmation)
- Edit account details

---

### 2. Transaction Types

Three distinct transaction types to solve the double-counting problem:

| Type | Description | Budget Impact | Example |
|------|-------------|---------------|---------|
| **Income** | Money coming in | Yes (+) | Salary deposit |
| **Expense** | Money going out (purchases) | Yes (-) | Grocery purchase |
| **Transfer** | Money between accounts | No | Credit card payment |

**The Double-Counting Solution:**
```
Traditional (Wrong):
  Day 1:  Swipe CC for $200 groceries  → -$200 expense
  Day 15: Pay CC from checking         → -$200 expense
  Total: -$400 (WRONG!)

My Budget AI (Correct):
  Day 1:  Swipe CC for $200 groceries  → -$200 expense (categorized)
  Day 15: Pay CC from checking         → $0 budget impact (transfer)
  Total: -$200 (CORRECT!)
```

**Transfer Mechanics:**
- Source account balance decreases
- Destination account balance increases (or debt decreases for CC)
- Net budget impact: $0
- **Overdraft Warning**: 7-day advance notice if transfer would overdraft source account

---

### 3. Data Input (MVP)

**CSV Import:**
- Single consistent schema across all bank exports
- User maps columns during first import per account
- Fields: date, amount, description, (transaction type inferred or specified)

---

### 4. Transaction Management

**Automated Categorization (Rule-Based for MVP):**

| Color | Category | Example Keywords |
|-------|----------|------------------|
| Red | Health | doctor, pharmacy, medical, hospital |
| Orange | Food & Drink | grocery, restaurant, uber eats, doordash |
| Yellow | Shopping | amazon, target, clothing, electronics |
| Green | Travel | airline, hotel, airbnb, booking |
| Blue | Transportation | gas, uber, lyft, parking, transit |
| Purple | Services | utility, subscription, netflix, spotify |
| Pink | Entertainment | movie, theater, concert, gaming |
| Gray | Uncategorized | (fallback) |

**Income:** Single bucket, no categorization needed.

**Manual Operations:**
- Override auto-assigned categories
- Add notes to transactions
- Search/filter by date, account, category, amount

---

### 5. Balance Tracking

**Credit Cards:**
- **Current Balance**: Running total of all transactions (real-time debt)
- **Statement Balance**: Auto-calculated snapshot at statement close date, editable
- Expenses increase debt, payments (transfers in) decrease debt

**Checking/Savings:**
- Running balance based on starting balance + transactions
- Income increases balance, expenses/transfers out decrease balance

**No overdraft protection on expenses** - only warn for transfers.

---

### 6. Billing Cycle Management

**Per Credit Card:**
- Track statement close date (day of month)
- Track payment due date (day of month)
- Auto-calculate statement balance at close

**Dashboard Alerts:**
- Show upcoming due dates with amounts owed
- **7-day advance warning** for approaching due dates
- Visual indicator for urgency

---

### 7. Reporting & Views

**Two Primary Financial Views:**

**A. Cash Flow Statement (Income vs. Expenses)**
- Period-based: week, month, year
- Shows: Total Income | Total Expenses | Net Cash Flow
- Ignores transfers entirely
- Example: "Income: $5,000 | Expenses: $3,200 | Net: +$1,800"

**B. Balance Sheet (Net Worth)**
- Point-in-time snapshot
- Assets: (Checking + Savings balances)
- Liabilities: (Credit Card balances)
- Net Worth: Assets - Liabilities

**Activity Analysis:**
- High-level totals by default
- Drill-down to per-category breakdowns
- Aggregates: weekly, monthly, yearly

**Dashboard Layout:**
- Combined view of all accounts (default)
- Per-account views in separate tabs
- Upcoming due dates prominently displayed

---

### 8. Notifications & Alerts

In-app only:
- Payment due date approaching (7 days out)
- Potential overdraft on pending transfers
- Expenses approaching income threshold

---

## Non-Functional Requirements

### Platform
Local web application (Python backend + React frontend, served on localhost)

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language (Backend) | Python 3.11 |
| Language (Frontend) | TypeScript |
| Package Management | UV (Python), npm (JS) |
| Configuration | pyproject.toml |
| Frontend Framework | React + Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| State Management | TanStack Query (React Query) |
| Routing | React Router v6 |
| Backend Framework | FastAPI |
| Data Processing | Pandas |
| Database | SQLite |
| Categorization (MVP) | Rule-based keyword matching |
| Linting | Ruff (Python), TypeScript strict mode |

### Performance
- ~50 transactions/month expected
- Pandas/SQLite are lightweight; no scaling concerns

### Usability
- Clean, modern web interface
- Responsive layout with sidebar navigation
- Color-coded categories

### Privacy
- Runs locally on localhost — no internet calls
- All data stored locally in SQLite

### Testing
- pytest for backend unit + integration tests
- TypeScript strict mode for frontend type safety
