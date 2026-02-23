"""FastAPI dependency injection — connection, repositories, and services."""

import sqlite3
from typing import Generator

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.statement_repo import StatementRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.services.alerts import AlertService
from src.services.balance_calculator import BalanceCalculator
from src.services.balance_sheet import BalanceSheetService
from src.services.cash_flow import CashFlowService
from src.services.categorizer import Categorizer
from src.services.importer import CsvImporter
from src.services.reports import ReportService
from src.services.statement_service import StatementService

# Module-level connection set by app lifespan
_conn: sqlite3.Connection | None = None


def set_connection(conn: sqlite3.Connection) -> None:
    global _conn
    _conn = conn


def get_conn() -> Generator[sqlite3.Connection, None, None]:
    assert _conn is not None, "Database connection not initialized"
    yield _conn


# Repositories

def get_account_repo(conn: sqlite3.Connection) -> AccountRepository:
    return AccountRepository(conn)


def get_transaction_repo(conn: sqlite3.Connection) -> TransactionRepository:
    return TransactionRepository(conn)


def get_category_repo(conn: sqlite3.Connection) -> CategoryRepository:
    return CategoryRepository(conn)


def get_statement_repo(conn: sqlite3.Connection) -> StatementRepository:
    return StatementRepository(conn)


# Services

def get_balance_calculator(
    account_repo: AccountRepository, transaction_repo: TransactionRepository
) -> BalanceCalculator:
    return BalanceCalculator(account_repo, transaction_repo)


def get_cash_flow_service(
    transaction_repo: TransactionRepository, category_repo: CategoryRepository
) -> CashFlowService:
    return CashFlowService(transaction_repo, category_repo)


def get_balance_sheet_service(
    account_repo: AccountRepository, balance_calc: BalanceCalculator
) -> BalanceSheetService:
    return BalanceSheetService(account_repo, balance_calc)


def get_alert_service(
    statement_repo: StatementRepository, account_repo: AccountRepository
) -> AlertService:
    return AlertService(statement_repo, account_repo)


def get_report_service(
    transaction_repo: TransactionRepository, category_repo: CategoryRepository
) -> ReportService:
    return ReportService(transaction_repo, category_repo)


def get_statement_service(
    account_repo: AccountRepository,
    statement_repo: StatementRepository,
    balance_calc: BalanceCalculator,
) -> StatementService:
    return StatementService(account_repo, statement_repo, balance_calc)


def get_categorizer(category_repo: CategoryRepository) -> Categorizer:
    categories = category_repo.get_all()
    return Categorizer(categories)


def get_csv_importer() -> CsvImporter:
    return CsvImporter()
