"""API integration tests using TestClient."""

import io
import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = ":memory:"

from src.api.app import app
from src.api.deps import set_connection
from src.database.connection import create_connection
from src.database.schema import initialize_database
from src.database.seeds import seed_categories


@pytest.fixture(autouse=True)
def setup_db():
    conn = create_connection(":memory:")
    initialize_database(conn)
    seed_categories(conn)
    set_connection(conn)
    yield
    conn.close()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=True)


# --- Categories ---

class TestCategories:
    def test_list_categories(self, client):
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8
        names = {c["name"] for c in data}
        assert "Food & Drink" in names
        assert "Uncategorized" in names


# --- Accounts ---

class TestAccounts:
    def _create_checking(self, client):
        return client.post("/api/accounts", json={
            "name": "Chase Checking", "type": "checking",
            "starting_balance": 5000.0,
        })

    def test_create_account(self, client):
        resp = self._create_checking(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Chase Checking"
        assert data["balance"] == 5000.0

    def test_list_accounts(self, client):
        self._create_checking(client)
        resp = client.get("/api/accounts")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_account(self, client):
        create_resp = self._create_checking(client)
        acct_id = create_resp.json()["id"]
        resp = client.get(f"/api/accounts/{acct_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Chase Checking"

    def test_get_account_not_found(self, client):
        resp = client.get("/api/accounts/999")
        assert resp.status_code == 404

    def test_update_account(self, client):
        create_resp = self._create_checking(client)
        acct_id = create_resp.json()["id"]
        resp = client.put(f"/api/accounts/{acct_id}", json={
            "name": "Updated", "type": "checking", "starting_balance": 6000.0,
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_delete_account(self, client):
        create_resp = self._create_checking(client)
        acct_id = create_resp.json()["id"]
        resp = client.delete(f"/api/accounts/{acct_id}")
        assert resp.status_code == 204
        resp = client.get(f"/api/accounts/{acct_id}")
        assert resp.status_code == 404


# --- Transactions ---

class TestTransactions:
    def _setup_account(self, client):
        resp = client.post("/api/accounts", json={
            "name": "Test Checking", "type": "checking",
            "starting_balance": 5000.0,
        })
        return resp.json()["id"]

    def test_create_transaction(self, client):
        acct_id = self._setup_account(client)
        resp = client.post("/api/transactions", json={
            "account_id": acct_id, "type": "expense",
            "amount": 50.0, "description": "Grocery Store",
            "date": "2025-01-15",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == 50.0
        assert data["category_id"] is not None  # auto-categorized

    def test_list_transactions(self, client):
        acct_id = self._setup_account(client)
        client.post("/api/transactions", json={
            "account_id": acct_id, "type": "expense",
            "amount": 50.0, "description": "Amazon Purchase",
            "date": "2025-01-15",
        })
        resp = client.get("/api/transactions")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_filter_by_account(self, client):
        acct_id = self._setup_account(client)
        client.post("/api/transactions", json={
            "account_id": acct_id, "type": "expense",
            "amount": 25.0, "description": "Coffee",
            "date": "2025-01-15",
        })
        resp = client.get(f"/api/transactions?account_id={acct_id}")
        assert len(resp.json()) == 1

    def test_update_transaction(self, client):
        acct_id = self._setup_account(client)
        create_resp = client.post("/api/transactions", json={
            "account_id": acct_id, "type": "expense",
            "amount": 50.0, "description": "Test",
            "date": "2025-01-15",
        })
        txn_id = create_resp.json()["id"]
        resp = client.put(f"/api/transactions/{txn_id}", json={
            "notes": "Updated note",
        })
        assert resp.status_code == 200
        assert resp.json()["notes"] == "Updated note"

    def test_delete_transaction(self, client):
        acct_id = self._setup_account(client)
        create_resp = client.post("/api/transactions", json={
            "account_id": acct_id, "type": "expense",
            "amount": 50.0, "description": "Test",
            "date": "2025-01-15",
        })
        txn_id = create_resp.json()["id"]
        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 204


# --- Dashboard ---

class TestDashboard:
    def test_empty_dashboard(self, client):
        resp = client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["accounts"] == []
        assert data["alerts"] == []
        assert data["cash_flow"]["total_income"] == 0
        assert data["balance_sheet"]["net_worth"] == 0


# --- Reports ---

class TestReports:
    def test_cash_flow(self, client):
        resp = client.get("/api/reports/cash-flow?start_date=2025-01-01&end_date=2025-12-31")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_income" in data

    def test_balance_sheet(self, client):
        resp = client.get("/api/reports/balance-sheet")
        assert resp.status_code == 200
        data = resp.json()
        assert "net_worth" in data

    def test_period_summary(self, client):
        resp = client.get("/api/reports/period-summary?start_date=2025-01-01&end_date=2025-01-31")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_income" in data


# --- Import ---

class TestImport:
    def _setup_account(self, client):
        resp = client.post("/api/accounts", json={
            "name": "Import Test", "type": "checking",
            "starting_balance": 1000.0,
        })
        return resp.json()["id"]

    def test_preview_import(self, client):
        acct_id = self._setup_account(client)
        csv_content = "date,amount,description\n2025-01-15,-50.00,Grocery Store\n2025-01-16,-25.00,Gas Station\n"
        resp = client.post(
            "/api/import/preview",
            data={"account_id": str(acct_id)},
            files={"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rows"] == 2
        assert len(data["transactions"]) == 2

    def test_confirm_import(self, client):
        acct_id = self._setup_account(client)
        resp = client.post("/api/import/confirm", json={
            "account_id": acct_id,
            "transactions": [
                {"account_id": acct_id, "type": "expense", "amount": 50.0,
                 "description": "Grocery Store", "date": "2025-01-15"},
            ],
        })
        assert resp.status_code == 200
        assert resp.json()["imported_count"] == 1

        txns = client.get(f"/api/transactions?account_id={acct_id}").json()
        assert len(txns) == 1
