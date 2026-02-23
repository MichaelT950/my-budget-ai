"""Tests for CsvImporter — type detection, amount normalization, validation."""

import os
import tempfile

from src.services.importer import CsvImporter


class TestCsvImporter:
    def _write_csv(self, content: str) -> str:
        """Write CSV content to a temp file and return path."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_basic_import(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,2500.00,DIRECT DEPOSIT ACME CORP\n"
            "2024-01-16,-45.23,WHOLE FOODS MARKET\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.total_rows == 2
            assert len(result.transactions) == 2
            assert len(result.errors) == 0
        finally:
            os.unlink(path)

    def test_income_keyword_detection(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,3500.00,DIRECT DEPOSIT ACME CORP\n"
            "2024-01-16,100.00,PAYROLL DEPOSIT\n"
            "2024-01-17,50.00,DIVIDEND PAYMENT\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert all(t.type == "income" for t in result.transactions)
        finally:
            os.unlink(path)

    def test_transfer_keyword_detection(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,-500.00,PAYMENT THANK YOU\n"
            "2024-01-16,-200.00,ONLINE TRANSFER TO SAVINGS\n"
            "2024-01-17,1200.00,AUTOPAY RECEIVED\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert all(t.type == "transfer" for t in result.transactions)
        finally:
            os.unlink(path)

    def test_expense_default_detection(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,-45.23,WHOLE FOODS MARKET\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.transactions[0].type == "expense"
        finally:
            os.unlink(path)

    def test_amount_normalization_negative_to_positive(self):
        """Negative amounts are stored as absolute values."""
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,-99.99,SOME EXPENSE\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.transactions[0].amount == 99.99
        finally:
            os.unlink(path)

    def test_explicit_type_column(self):
        path = self._write_csv(
            "date,amount,description,type\n"
            "01/15/2024,2500.00,PAYCHECK,income\n"
            "01/16/2024,45.23,GROCERY STORE,expense\n"
            "01/17/2024,500.00,CC PAYMENT,transfer\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.transactions[0].type == "income"
            assert result.transactions[1].type == "expense"
            assert result.transactions[2].type == "transfer"
        finally:
            os.unlink(path)

    def test_rejects_future_dates(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2099-01-15,100.00,FUTURE TRANSACTION\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert len(result.transactions) == 0
            assert len(result.errors) == 1
            assert "Future date" in result.errors[0]
        finally:
            os.unlink(path)

    def test_rejects_zero_amount(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,0,ZERO AMOUNT\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert len(result.transactions) == 0
            assert "zero" in result.errors[0].lower()
        finally:
            os.unlink(path)

    def test_rejects_empty_description(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,100.00,\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert len(result.transactions) == 0
            assert "description" in result.errors[0].lower()
        finally:
            os.unlink(path)

    def test_rejects_invalid_date(self):
        path = self._write_csv(
            "date,amount,description\n"
            "not-a-date,100.00,SOME PURCHASE\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert len(result.transactions) == 0
            assert "date" in result.errors[0].lower()
        finally:
            os.unlink(path)

    def test_mm_dd_yyyy_date_format(self):
        path = self._write_csv(
            "date,amount,description\n"
            "01/15/2024,100.00,PURCHASE\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.transactions[0].date == "2024-01-15"
        finally:
            os.unlink(path)

    def test_unpadded_m_d_yyyy_date_format(self):
        """M/D/YYYY (no leading zeros) should parse correctly — spec requirement."""
        path = self._write_csv(
            "date,amount,description\n"
            "1/5/2024,75.00,UNPADDED DATE PURCHASE\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert len(result.transactions) == 1
            assert result.transactions[0].date == "2024-01-05"
        finally:
            os.unlink(path)

    def test_mixed_valid_and_invalid_rows(self):
        path = self._write_csv(
            "date,amount,description\n"
            "2024-01-15,100.00,VALID PURCHASE\n"
            "bad-date,50.00,BAD DATE\n"
            "2024-01-17,0,ZERO AMOUNT\n"
            "2024-01-18,25.00,ANOTHER VALID\n"
        )
        try:
            result = CsvImporter().import_csv(path, account_id=1)
            assert result.total_rows == 4
            assert len(result.transactions) == 2
            assert len(result.errors) == 2
        finally:
            os.unlink(path)
