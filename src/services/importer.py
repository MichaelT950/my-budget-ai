"""CSV import service — parses bank CSVs into Transaction objects."""

from dataclasses import dataclass, field

import pandas as pd

from src.models.transaction import Transaction
from src.utils.date_helpers import is_future_date, parse_date

INCOME_KEYWORDS = [
    "DIRECT DEPOSIT", "PAYROLL", "SALARY", "TAX REFUND",
    "INTEREST PAYMENT", "DIVIDEND",
]

TRANSFER_KEYWORDS = [
    "PAYMENT THANK YOU", "AUTOPAY", "PAYMENT - THANK",
    "ONLINE TRANSFER", "TRANSFER TO", "TRANSFER FROM",
]


@dataclass
class ImportResult:
    transactions: list[Transaction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_rows: int = 0


class CsvImporter:
    """Parse CSV files into validated Transaction objects."""

    def import_csv(self, file_path: str, account_id: int) -> ImportResult:
        result = ImportResult()
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            result.errors.append(f"Failed to read CSV: {e}")
            return result

        # Normalize column names to lowercase
        df.columns = [c.strip().lower() for c in df.columns]

        if "date" not in df.columns or "amount" not in df.columns or "description" not in df.columns:
            result.errors.append("CSV must have 'date', 'amount', and 'description' columns")
            return result

        has_type_column = "type" in df.columns
        result.total_rows = len(df)

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed + header row
            errors: list[str] = []

            # Validate description
            description = str(row["description"]).strip()
            if not description or description == "nan":
                errors.append(f"Row {row_num}: Empty description - skipped")
                result.errors.extend(errors)
                continue

            # Validate and parse amount
            try:
                raw_amount = float(row["amount"])
            except (ValueError, TypeError):
                errors.append(f"Row {row_num}: Invalid amount - skipped")
                result.errors.extend(errors)
                continue

            if raw_amount == 0:
                errors.append(f"Row {row_num}: Amount is zero - skipped")
                result.errors.extend(errors)
                continue

            # Validate and parse date
            try:
                parsed_date = parse_date(str(row["date"]))
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date {row['date']!r} - skipped")
                result.errors.extend(errors)
                continue

            if is_future_date(parsed_date):
                errors.append(f"Row {row_num}: Future date {parsed_date} - skipped")
                result.errors.extend(errors)
                continue

            # Determine transaction type
            if has_type_column and pd.notna(row.get("type")):
                txn_type = str(row["type"]).strip().lower()
                if txn_type not in ("income", "expense", "transfer"):
                    txn_type = self._detect_type(description, raw_amount)
            else:
                txn_type = self._detect_type(description, raw_amount)

            result.transactions.append(Transaction(
                account_id=account_id,
                type=txn_type,
                amount=abs(raw_amount),
                description=description,
                date=parsed_date.isoformat(),
            ))

        return result

    def _detect_type(self, description: str, amount: float) -> str:
        """Infer transaction type from description keywords and amount sign."""
        desc_upper = description.upper()
        for keyword in INCOME_KEYWORDS:
            if keyword in desc_upper:
                return "income"
        for keyword in TRANSFER_KEYWORDS:
            if keyword in desc_upper:
                return "transfer"
        # Positive amounts without keyword match could be income,
        # but default to expense per spec (most transactions are expenses)
        return "expense"
