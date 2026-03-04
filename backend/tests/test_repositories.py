"""Tests for all 4 repository classes — CRUD, FK constraints, date filtering, JSON round-trip."""

import sqlite3

import pytest

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.statement_repo import StatementRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.models.account import Account
from src.models.statement import StatementSnapshot
from src.models.transaction import Transaction

# --- Category Repository ---


class TestCategoryRepository:
    def test_get_all_returns_seeded_categories(self, conn):
        repo = CategoryRepository(conn)
        categories = repo.get_all()
        assert len(categories) == 8
        names = {c.name for c in categories}
        assert "Health" in names
        assert "Uncategorized" in names

    def test_get_by_id(self, conn):
        repo = CategoryRepository(conn)
        cat = repo.get_by_id(1)
        assert cat is not None
        assert cat.id == 1

    def test_get_by_name(self, conn):
        repo = CategoryRepository(conn)
        cat = repo.get_by_name("Food & Drink")
        assert cat is not None
        assert cat.color == "orange"

    def test_get_by_name_not_found(self, conn):
        repo = CategoryRepository(conn)
        assert repo.get_by_name("NonExistent") is None

    def test_keywords_json_round_trip(self, conn):
        """Keywords stored as JSON are parsed back into list[str]."""
        repo = CategoryRepository(conn)
        cat = repo.get_by_name("Health")
        assert isinstance(cat.keywords, list)
        assert "doctor" in cat.keywords
        assert "pharmacy" in cat.keywords

    def test_uncategorized_has_empty_keywords(self, conn):
        repo = CategoryRepository(conn)
        cat = repo.get_by_name("Uncategorized")
        assert cat.keywords == []


# --- Account Repository ---


class TestAccountRepository:
    def test_create_and_get(self, conn):
        repo = AccountRepository(conn)
        acct = repo.create(Account(name="Chase Checking", type="checking", starting_balance=1000.0))
        assert acct.id is not None
        fetched = repo.get_by_id(acct.id)
        assert fetched.name == "Chase Checking"
        assert fetched.type == "checking"
        assert fetched.starting_balance == 1000.0

    def test_create_credit_card(self, conn):
        repo = AccountRepository(conn)
        acct = repo.create(Account(
            name="Chase Sapphire", type="credit_card", starting_balance=500.0,
            credit_limit=10000.0, statement_close_day=15, payment_due_day=10,
        ))
        fetched = repo.get_by_id(acct.id)
        assert fetched.credit_limit == 10000.0
        assert fetched.statement_close_day == 15

    def test_get_all(self, conn):
        repo = AccountRepository(conn)
        repo.create(Account(name="Acct A", type="checking"))
        repo.create(Account(name="Acct B", type="savings"))
        assert len(repo.get_all()) == 2

    def test_update(self, conn):
        repo = AccountRepository(conn)
        acct = repo.create(Account(name="Old Name", type="checking"))
        acct.name = "New Name"
        repo.update(acct)
        fetched = repo.get_by_id(acct.id)
        assert fetched.name == "New Name"

    def test_delete(self, conn):
        repo = AccountRepository(conn)
        acct = repo.create(Account(name="To Delete", type="checking"))
        assert repo.delete(acct.id)
        assert repo.get_by_id(acct.id) is None

    def test_delete_nonexistent(self, conn):
        repo = AccountRepository(conn)
        assert not repo.delete(9999)

    def test_unique_name_constraint(self, conn):
        repo = AccountRepository(conn)
        repo.create(Account(name="Same Name", type="checking"))
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(Account(name="Same Name", type="savings"))

    def test_invalid_type_rejected(self, conn):
        repo = AccountRepository(conn)
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(Account(name="Bad", type="invalid_type"))


# --- Transaction Repository ---


class TestTransactionRepository:
    @pytest.fixture
    def checking_account(self, conn):
        repo = AccountRepository(conn)
        return repo.create(Account(name="Checking", type="checking", starting_balance=5000.0))

    @pytest.fixture
    def category_id(self, conn):
        repo = CategoryRepository(conn)
        return repo.get_by_name("Food & Drink").id

    def test_create_and_get(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        txn = repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=45.23,
            description="WHOLE FOODS", category_id=category_id, date="2024-01-15",
        ))
        assert txn.id is not None
        txns = repo.get_by_account(checking_account.id)
        assert len(txns) == 1
        assert txns[0].amount == 45.23

    def test_create_many(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        txns = [
            Transaction(account_id=checking_account.id, type="expense", amount=10.0,
                        description="Item 1", category_id=category_id, date="2024-01-01"),
            Transaction(account_id=checking_account.id, type="income", amount=3000.0,
                        description="Paycheck", date="2024-01-01"),
        ]
        created = repo.create_many(txns)
        assert all(t.id is not None for t in created)
        assert len(repo.get_all()) == 2

    def test_date_filtering(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=10.0,
            description="Jan", category_id=category_id, date="2024-01-15",
        ))
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=20.0,
            description="Feb", category_id=category_id, date="2024-02-15",
        ))
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=30.0,
            description="Mar", category_id=category_id, date="2024-03-15",
        ))
        jan_feb = repo.get_by_account(checking_account.id, start_date="2024-01-01", end_date="2024-02-28")
        assert len(jan_feb) == 2

    def test_get_all_with_date_range(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=10.0,
            description="Jan", category_id=category_id, date="2024-01-15",
        ))
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=20.0,
            description="Mar", category_id=category_id, date="2024-03-15",
        ))
        jan_only = repo.get_all(start_date="2024-01-01", end_date="2024-01-31")
        assert len(jan_only) == 1

    def test_update(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        txn = repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=10.0,
            description="Original", category_id=category_id, date="2024-01-15",
        ))
        txn.description = "Updated"
        txn.notes = "edited"
        repo.update(txn)
        fetched = repo.get_by_account(checking_account.id)[0]
        assert fetched.description == "Updated"
        assert fetched.notes == "edited"

    def test_delete(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        txn = repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=10.0,
            description="To delete", category_id=category_id, date="2024-01-15",
        ))
        assert repo.delete(txn.id)
        assert len(repo.get_by_account(checking_account.id)) == 0

    def test_fk_constraint_invalid_account(self, conn, category_id):
        """FK constraint prevents transaction with nonexistent account."""
        repo = TransactionRepository(conn)
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(Transaction(
                account_id=9999, type="expense", amount=10.0,
                description="Bad FK", category_id=category_id, date="2024-01-15",
            ))

    def test_amount_must_be_positive(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(Transaction(
                account_id=checking_account.id, type="expense", amount=-10.0,
                description="Negative", category_id=category_id, date="2024-01-15",
            ))

    def test_invalid_type_rejected(self, conn, checking_account, category_id):
        repo = TransactionRepository(conn)
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(Transaction(
                account_id=checking_account.id, type="invalid", amount=10.0,
                description="Bad type", category_id=category_id, date="2024-01-15",
            ))

    def test_find_duplicates_detects_existing(self, conn, checking_account, category_id):
        """find_duplicates returns True for transactions matching existing records."""
        repo = TransactionRepository(conn)
        repo.create(Transaction(
            account_id=checking_account.id, type="expense", amount=50.0,
            description="WHOLE FOODS", category_id=category_id, date="2024-01-15",
        ))
        candidates = [
            Transaction(account_id=checking_account.id, type="expense", amount=50.0,
                        description="WHOLE FOODS", date="2024-01-15"),
            Transaction(account_id=checking_account.id, type="expense", amount=25.0,
                        description="GAS STATION", date="2024-01-16"),
        ]
        flags = repo.find_duplicates(checking_account.id, candidates)
        assert flags == [True, False]

    def test_find_duplicates_empty_db(self, conn, checking_account):
        """find_duplicates returns all False when no transactions exist."""
        repo = TransactionRepository(conn)
        candidates = [
            Transaction(account_id=checking_account.id, type="expense", amount=50.0,
                        description="WHOLE FOODS", date="2024-01-15"),
        ]
        flags = repo.find_duplicates(checking_account.id, candidates)
        assert flags == [False]

    def test_find_duplicates_different_account(self, conn, checking_account, category_id):
        """Transactions on a different account are not considered duplicates."""
        repo = TransactionRepository(conn)
        acct_repo = AccountRepository(conn)
        other = acct_repo.create(Account(name="Savings", type="savings"))
        repo.create(Transaction(
            account_id=other.id, type="expense", amount=50.0,
            description="WHOLE FOODS", category_id=category_id, date="2024-01-15",
        ))
        candidates = [
            Transaction(account_id=checking_account.id, type="expense", amount=50.0,
                        description="WHOLE FOODS", date="2024-01-15"),
        ]
        flags = repo.find_duplicates(checking_account.id, candidates)
        assert flags == [False]


# --- Statement Repository ---


class TestStatementRepository:
    @pytest.fixture
    def cc_account(self, conn):
        repo = AccountRepository(conn)
        return repo.create(Account(
            name="Chase CC", type="credit_card", starting_balance=0.0,
            credit_limit=5000.0, statement_close_day=15, payment_due_day=10,
        ))

    def test_create_and_get(self, conn, cc_account):
        repo = StatementRepository(conn)
        snap = repo.create(StatementSnapshot(
            account_id=cc_account.id, statement_date="2024-01-15",
            balance=1234.56, due_date="2024-02-10",
        ))
        assert snap.id is not None
        stmts = repo.get_by_account(cc_account.id)
        assert len(stmts) == 1
        assert stmts[0].balance == 1234.56

    def test_get_unpaid(self, conn, cc_account):
        repo = StatementRepository(conn)
        repo.create(StatementSnapshot(
            account_id=cc_account.id, statement_date="2024-01-15",
            balance=500.0, due_date="2024-02-10",
        ))
        repo.create(StatementSnapshot(
            account_id=cc_account.id, statement_date="2024-02-15",
            balance=600.0, due_date="2024-03-10", is_paid=True,
        ))
        unpaid = repo.get_unpaid()
        assert len(unpaid) == 1
        assert unpaid[0].balance == 500.0

    def test_mark_paid(self, conn, cc_account):
        repo = StatementRepository(conn)
        snap = repo.create(StatementSnapshot(
            account_id=cc_account.id, statement_date="2024-01-15",
            balance=500.0, due_date="2024-02-10",
        ))
        assert repo.mark_paid(snap.id)
        unpaid = repo.get_unpaid()
        assert len(unpaid) == 0

    def test_unique_constraint_account_date(self, conn, cc_account):
        """Can't have two statements for same account on same date."""
        repo = StatementRepository(conn)
        repo.create(StatementSnapshot(
            account_id=cc_account.id, statement_date="2024-01-15",
            balance=500.0, due_date="2024-02-10",
        ))
        with pytest.raises(sqlite3.IntegrityError):
            repo.create(StatementSnapshot(
                account_id=cc_account.id, statement_date="2024-01-15",
                balance=600.0, due_date="2024-02-10",
            ))
