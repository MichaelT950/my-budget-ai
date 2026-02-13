"""Dashboard view — summary bar, account cards, recent transactions."""

import tkinter as tk
from datetime import date
from tkinter import ttk

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.services.balance_calculator import BalanceCalculator
from src.ui.components.data_table import DataTable
from src.ui.theme import FONTS, SPACING, TYPE_COLORS
from src.utils.formatters import format_currency, format_signed_currency


class DashboardView(ttk.Frame):
    def __init__(self, parent, conn, **kwargs):
        super().__init__(parent, **kwargs)
        self.conn = conn
        self.account_repo = AccountRepository(conn)
        self.txn_repo = TransactionRepository(conn)
        self.category_repo = CategoryRepository(conn)
        self.balance_calc = BalanceCalculator(self.account_repo, self.txn_repo)
        self._build_ui()

    def _build_ui(self):
        # Title
        title = ttk.Label(self, text="Dashboard", font=FONTS["heading"])
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        # Summary bar
        self.summary_frame = ttk.LabelFrame(self, text="Summary", padding=SPACING["sm"])
        self.summary_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        # Accounts section
        self.accounts_frame = ttk.LabelFrame(self, text="Accounts", padding=SPACING["sm"])
        self.accounts_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        # Recent transactions
        txn_label = ttk.Label(self, text="Recent Transactions", font=FONTS["subheading"])
        txn_label.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        self.txn_table = DataTable(self, columns=[
            ("date", "Date", 100),
            ("account", "Account", 140),
            ("description", "Description", 250),
            ("category", "Category", 120),
            ("type", "Type", 80),
            ("amount", "Amount", 100),
        ])
        self.txn_table.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Configure row colors for transaction types
        for type_name, color in TYPE_COLORS.items():
            self.txn_table.tree.tag_configure(type_name, foreground=color)

        self.refresh()

    def refresh(self):
        self._refresh_summary()
        self._refresh_accounts()
        self._refresh_transactions()

    def _refresh_summary(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        accounts = self.account_repo.get_all()
        balances = self.balance_calc.get_all_balances()

        total_assets = sum(
            balances.get(a.id, 0) for a in accounts if a.type in ("checking", "savings")
        )
        total_liabilities = sum(
            balances.get(a.id, 0) for a in accounts if a.type == "credit_card"
        )
        net_worth = total_assets - total_liabilities

        # Current month income/expenses
        today = date.today()
        month_start = today.replace(day=1).isoformat()
        month_txns = self.txn_repo.get_all(start_date=month_start)
        month_income = sum(t.amount for t in month_txns if t.type == "income")
        month_expenses = sum(t.amount for t in month_txns if t.type == "expense")
        month_net = month_income - month_expenses

        items = [
            ("Total Assets", format_currency(total_assets), "#43A047"),
            ("Total Liabilities", format_currency(total_liabilities), "#E53935"),
            ("Net Worth", format_currency(net_worth), "#1E88E5"),
            ("Month Income", format_currency(month_income), "#43A047"),
            ("Month Expenses", format_currency(month_expenses), "#E53935"),
            ("Month Net", format_currency(month_net), "#1E88E5" if month_net >= 0 else "#E53935"),
        ]

        for i, (label_text, value, color) in enumerate(items):
            frame = ttk.Frame(self.summary_frame)
            frame.grid(row=0, column=i, padx=SPACING["sm"], pady=SPACING["xs"])
            ttk.Label(frame, text=label_text, font=FONTS["small"]).pack()
            val_label = tk.Label(frame, text=value, font=FONTS["subheading"], fg=color)
            val_label.pack()

    def _refresh_accounts(self):
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()

        accounts = self.account_repo.get_all()
        balances = self.balance_calc.get_all_balances()

        if not accounts:
            ttk.Label(self.accounts_frame, text="No accounts yet. Add one from the Accounts tab.",
                      font=FONTS["body"]).pack(pady=SPACING["sm"])
            return

        for i, acct in enumerate(accounts):
            balance = balances.get(acct.id, 0)
            type_label = acct.type.replace("_", " ").title()
            color = "#E53935" if acct.type == "credit_card" else "#43A047"

            frame = ttk.Frame(self.accounts_frame)
            frame.grid(row=i // 3, column=i % 3, padx=SPACING["sm"], pady=SPACING["xs"], sticky="w")
            ttk.Label(frame, text=acct.name, font=FONTS["body"]).pack(anchor="w")
            ttk.Label(frame, text=type_label, font=FONTS["small"]).pack(anchor="w")
            tk.Label(frame, text=format_currency(balance), font=FONTS["subheading"], fg=color).pack(anchor="w")

    def _refresh_transactions(self):
        self.txn_table.clear()
        txns = self.txn_repo.get_all()[:50]

        accounts = {a.id: a.name for a in self.account_repo.get_all()}
        categories = {c.id: c.name for c in self.category_repo.get_all()}

        for txn in txns:
            acct_name = accounts.get(txn.account_id, "Unknown")
            cat_name = categories.get(txn.category_id, "") if txn.category_id else ""
            amount_str = format_signed_currency(txn.amount, txn.type)

            self.txn_table.insert_row(
                values=(txn.date, acct_name, txn.description, cat_name, txn.type, amount_str),
                tags=(txn.type,),
            )
