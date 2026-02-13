"""My Budget AI — Personal budget tracking application."""

import sys

from src.database.connection import close_connection, get_connection
from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.statement_repo import StatementRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.database.schema import initialize_database
from src.database.seeds import seed_categories
from src.services.balance_calculator import BalanceCalculator
from src.services.statement_service import StatementService
from src.ui.app import App
from src.ui.views.accounts import AccountsView
from src.ui.views.dashboard import DashboardView
from src.ui.views.import_csv import ImportCsvView
from src.ui.views.reports import ReportsView
from src.ui.views.transactions import TransactionsView


def main():
    print("My Budget AI — starting up...")

    conn = get_connection()
    initialize_database(conn)
    seed_categories(conn)

    # Auto-create statement snapshots for CC accounts
    acct_repo = AccountRepository(conn)
    stmt_repo = StatementRepository(conn)
    txn_repo = TransactionRepository(conn)
    balance_calc = BalanceCalculator(acct_repo, txn_repo)
    stmt_svc = StatementService(acct_repo, stmt_repo, balance_calc)
    stmt_svc.auto_create_statements()

    app = App(conn)

    def on_data_change():
        """Refresh all instantiated views when data changes."""
        for view in app._views.values():
            if hasattr(view, "refresh"):
                view.refresh()

    app.register_view("Dashboard", lambda parent, c: DashboardView(parent, c))
    app.register_view("Accounts", lambda parent, c: AccountsView(parent, c, on_change=on_data_change))
    app.register_view("Transactions", lambda parent, c: TransactionsView(parent, c, on_change=on_data_change))
    app.register_view("Import CSV", lambda parent, c: ImportCsvView(parent, c, on_change=on_data_change))
    app.register_view("Reports", lambda parent, c: ReportsView(parent, c))

    app.show_view("Dashboard")

    def on_close():
        close_connection()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
