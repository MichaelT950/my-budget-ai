# CSV Import Schema

## Overview

For MVP, all bank exports should follow a single consistent schema. This document defines the expected CSV format.

---

## Required Format

### Columns

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| date | Yes | String (YYYY-MM-DD or MM/DD/YYYY) | Transaction date |
| amount | Yes | Number | Transaction amount (see sign convention below) |
| description | Yes | String | Transaction description from bank |
| type | No | String | "income", "expense", or "transfer" (auto-detected if missing) |

### Example CSV

```csv
date,amount,description,type
2024-01-15,2500.00,DIRECT DEPOSIT - ACME CORP,income
2024-01-16,-45.23,WHOLE FOODS MARKET #123,expense
2024-01-17,-12.99,NETFLIX SUBSCRIPTION,expense
2024-01-18,-35.00,SHELL GAS STATION,expense
2024-01-20,-500.00,PAYMENT THANK YOU,transfer
```

---

## Amount Sign Convention

The importer will handle both conventions:

### Convention A: Signed Amounts (Preferred)
- Negative = money out (expenses, transfers out)
- Positive = money in (income, transfers in)

```csv
date,amount,description
2024-01-15,2500.00,DIRECT DEPOSIT    # Positive = income
2024-01-16,-45.23,WHOLE FOODS        # Negative = expense
```

### Convention B: Absolute Amounts with Type
- All amounts positive
- Type column specifies direction

```csv
date,amount,description,type
2024-01-15,2500.00,DIRECT DEPOSIT,income
2024-01-16,45.23,WHOLE FOODS,expense
```

---

## Type Detection Logic

If `type` column is missing, the importer will infer:

1. **Explicit keywords for income:**
   - "DIRECT DEPOSIT"
   - "PAYROLL"
   - "SALARY"
   - "TAX REFUND"
   - "INTEREST PAYMENT"
   - "DIVIDEND"

2. **Explicit keywords for transfers:**
   - "PAYMENT THANK YOU"
   - "AUTOPAY"
   - "PAYMENT - THANK"
   - "ONLINE TRANSFER"
   - "TRANSFER TO"
   - "TRANSFER FROM"

3. **Everything else:** Expense

---

## Date Parsing

The importer supports multiple date formats:

| Format | Example |
|--------|---------|
| YYYY-MM-DD | 2024-01-15 |
| MM/DD/YYYY | 01/15/2024 |
| MM-DD-YYYY | 01-15-2024 |
| M/D/YYYY | 1/15/2024 |

---

## Import Workflow

```
┌─────────────────┐
│ Select CSV File │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Select Target       │
│ Account             │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Preview Transactions│
│ (First 10 rows)     │
│ - Auto-categorized  │
│ - Type detected     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Confirm Import      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Transactions Added  │
│ Account Balance     │
│ Updated             │
└─────────────────────┘
```

---

## Transfer Handling

### Credit Card Payments (Special Case)

When importing to a **checking account** and a transaction looks like a credit card payment:
- Mark as type = "transfer"
- Prompt user: "Which credit card was this payment for?"
- Set `transfer_to_account_id` to the selected credit card

**Detection keywords:**
- Card name in description (e.g., "CHASE CARD PAYMENT")
- Generic payment terms followed by card-like patterns

### Between Own Accounts

When importing and a transaction looks like an internal transfer:
- Mark as type = "transfer"
- Prompt user to select the destination account

---

## Validation Rules

1. **Date**: Must be parseable, cannot be in the future
2. **Amount**: Must be a valid number, cannot be zero
3. **Description**: Cannot be empty

### Error Handling

```
Row 15: Invalid date "not-a-date" - skipped
Row 23: Amount is zero - skipped
Row 45: Empty description - skipped

Import Summary:
  Total rows: 50
  Imported: 47
  Skipped: 3
```

---

## Sample Files

### Checking Account Export
```csv
date,amount,description
2024-01-01,3500.00,DIRECT DEPOSIT ACME CORP
2024-01-03,-1200.00,CHASE CARD PAYMENT
2024-01-05,-150.00,TRANSFER TO SAVINGS
2024-01-10,-85.50,CHECK #1234
2024-01-15,3500.00,DIRECT DEPOSIT ACME CORP
```

### Credit Card Export
```csv
date,amount,description
2024-01-02,-45.23,WHOLE FOODS MARKET
2024-01-03,-12.99,SPOTIFY SUBSCRIPTION
2024-01-04,-89.00,AMAZON.COM
2024-01-05,-15.00,STARBUCKS
2024-01-06,1200.00,PAYMENT THANK YOU
```

Note: For credit cards, positive amounts are payments (transfers in, reducing debt).

---

## Future Enhancements (Post-MVP)

1. **Column Mapping UI**: Allow user to map any CSV column to the expected fields
2. **Save Mappings**: Remember column mappings per bank for future imports
3. **Duplicate Detection**: Warn if transaction appears to already exist
4. **Multi-file Import**: Import multiple CSVs at once
