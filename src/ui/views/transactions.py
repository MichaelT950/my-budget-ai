"""Transactions view — search, filter, inline edit category and notes."""

import tkinter as tk
from tkinter import messagebox, ttk

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.ui.components.data_table import DataTable
from src.ui.theme import FONTS, SPACING, TYPE_COLORS
from src.utils.formatters import format_signed_currency


class TransactionsView(ttk.Frame):
    def __init__(self, parent, conn, on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.conn = conn
        self.account_repo = AccountRepository(conn)
        self.txn_repo = TransactionRepository(conn)
        self.category_repo = CategoryRepository(conn)
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Transactions", font=FONTS["heading"])
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        # Filter controls
        filter_frame = ttk.LabelFrame(self, text="Filters", padding=SPACING["sm"])
        filter_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        # Date range
        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, padx=4, pady=2)
        self.start_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=4)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, padx=4, pady=2)
        self.end_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3, padx=4)

        # Account filter
        ttk.Label(filter_frame, text="Account:").grid(row=0, column=4, padx=4, pady=2)
        self.acct_filter_var = tk.StringVar(value="All")
        self.acct_filter_combo = ttk.Combobox(filter_frame, textvariable=self.acct_filter_var,
                                               state="readonly", width=18)
        self.acct_filter_combo.grid(row=0, column=5, padx=4)

        # Category filter
        ttk.Label(filter_frame, text="Category:").grid(row=0, column=6, padx=4, pady=2)
        self.cat_filter_var = tk.StringVar(value="All")
        self.cat_filter_combo = ttk.Combobox(filter_frame, textvariable=self.cat_filter_var,
                                              state="readonly", width=16)
        self.cat_filter_combo.grid(row=0, column=7, padx=4)

        ttk.Button(filter_frame, text="Apply", command=self._apply_filters).grid(row=0, column=8, padx=8)
        ttk.Button(filter_frame, text="Clear", command=self._clear_filters).grid(row=0, column=9, padx=4)

        # Transaction table
        self.table = DataTable(self, columns=[
            ("id", "ID", 40),
            ("date", "Date", 100),
            ("account", "Account", 140),
            ("description", "Description", 220),
            ("category", "Category", 120),
            ("type", "Type", 80),
            ("amount", "Amount", 100),
            ("notes", "Notes", 150),
        ])
        self.table.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        for type_name, color in TYPE_COLORS.items():
            self.table.tree.tag_configure(type_name, foreground=color)

        # Edit controls
        edit_frame = ttk.LabelFrame(self, text="Edit Selected", padding=SPACING["sm"])
        edit_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        ttk.Label(edit_frame, text="Category:").pack(side=tk.LEFT, padx=4)
        self.edit_cat_var = tk.StringVar()
        self.edit_cat_combo = ttk.Combobox(edit_frame, textvariable=self.edit_cat_var,
                                            state="readonly", width=18)
        self.edit_cat_combo.pack(side=tk.LEFT, padx=4)

        ttk.Label(edit_frame, text="Notes:").pack(side=tk.LEFT, padx=4)
        self.edit_notes_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.edit_notes_var, width=30).pack(side=tk.LEFT, padx=4)

        ttk.Button(edit_frame, text="Save", command=self._save_edit).pack(side=tk.LEFT, padx=8)

        self.refresh()

    def refresh(self):
        self._refresh_filter_options()
        self._load_transactions()

    def _refresh_filter_options(self):
        accounts = self.account_repo.get_all()
        self._accounts = {a.name: a for a in accounts}
        self.acct_filter_combo["values"] = ["All"] + [a.name for a in accounts]

        categories = self.category_repo.get_all()
        self._categories = {c.name: c for c in categories}
        self._categories_by_id = {c.id: c for c in categories}
        self.cat_filter_combo["values"] = ["All"] + [c.name for c in categories]
        self.edit_cat_combo["values"] = [c.name for c in categories]

    def _load_transactions(self):
        self.table.clear()

        start = self.start_date_var.get() or None
        end = self.end_date_var.get() or None

        acct_name = self.acct_filter_var.get()
        if acct_name != "All" and acct_name in self._accounts:
            acct = self._accounts[acct_name]
            txns = self.txn_repo.get_by_account(acct.id, start, end)
        else:
            txns = self.txn_repo.get_all(start, end)

        cat_filter = self.cat_filter_var.get()
        if cat_filter != "All" and cat_filter in self._categories:
            filter_cat_id = self._categories[cat_filter].id
            txns = [t for t in txns if t.category_id == filter_cat_id]

        accounts = {a.id: a.name for a in self.account_repo.get_all()}
        self._txn_map = {}

        for txn in txns:
            acct_display = accounts.get(txn.account_id, "Unknown")
            cat = self._categories_by_id.get(txn.category_id)
            cat_name = cat.name if cat else ""
            amount_str = format_signed_currency(txn.amount, txn.type)

            item_id = self.table.insert_row(
                values=(txn.id, txn.date, acct_display, txn.description,
                        cat_name, txn.type, amount_str, txn.notes or ""),
                tags=(txn.type,),
            )
            self._txn_map[item_id] = txn

    def _apply_filters(self):
        self._load_transactions()

    def _clear_filters(self):
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.acct_filter_var.set("All")
        self.cat_filter_var.set("All")
        self._load_transactions()

    def _save_edit(self):
        selection = self.table.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a transaction to edit.")
            return

        item_id = selection[0]
        txn = self._txn_map.get(item_id)
        if not txn:
            return

        cat_name = self.edit_cat_var.get()
        if cat_name and cat_name in self._categories:
            txn.category_id = self._categories[cat_name].id

        notes = self.edit_notes_var.get().strip()
        if notes:
            txn.notes = notes

        self.txn_repo.update(txn)
        self._load_transactions()
        if self.on_change:
            self.on_change()
