"""Accounts view — list, add, edit, delete accounts."""

import tkinter as tk
from tkinter import messagebox, ttk

from src.database.repositories.account_repo import AccountRepository
from src.models.account import Account
from src.services.balance_calculator import BalanceCalculator
from src.ui.components.data_table import DataTable
from src.ui.theme import FONTS, SPACING
from src.utils.formatters import format_currency


class AccountsView(ttk.Frame):
    def __init__(self, parent, conn, on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.conn = conn
        self.account_repo = AccountRepository(conn)
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Accounts", font=FONTS["heading"])
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        # Account list
        self.table = DataTable(self, columns=[
            ("name", "Name", 180),
            ("type", "Type", 120),
            ("balance", "Balance", 120),
            ("credit_limit", "Credit Limit", 120),
            ("close_day", "Close Day", 80),
            ("due_day", "Due Day", 80),
        ])
        self.table.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])
        ttk.Button(btn_frame, text="Add Account", command=self._show_add_form).pack(side=tk.LEFT, padx=SPACING["xs"])
        ttk.Button(btn_frame, text="Edit", command=self._edit_selected).pack(side=tk.LEFT, padx=SPACING["xs"])
        ttk.Button(btn_frame, text="Delete", command=self._delete_selected).pack(side=tk.LEFT, padx=SPACING["xs"])

        # Add/Edit form (hidden initially)
        self.form_frame = ttk.LabelFrame(self, text="Add Account", padding=SPACING["sm"])
        self._build_form()

        self.refresh()

    def _build_form(self):
        self.form_vars = {}

        row = 0
        for label, var_name in [("Name:", "name"), ("Starting Balance:", "starting_balance")]:
            ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar()
            ttk.Entry(self.form_frame, textvariable=var, width=30).grid(row=row, column=1, padx=4, pady=2)
            self.form_vars[var_name] = var
            row += 1

        # Type dropdown
        ttk.Label(self.form_frame, text="Type:").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        self.form_vars["type"] = tk.StringVar(value="checking")
        type_combo = ttk.Combobox(self.form_frame, textvariable=self.form_vars["type"],
                                  values=["checking", "savings", "credit_card"], state="readonly", width=27)
        type_combo.grid(row=row, column=1, padx=4, pady=2)
        type_combo.bind("<<ComboboxSelected>>", self._on_type_change)
        row += 1

        # CC-specific fields
        self.cc_fields_frame = ttk.Frame(self.form_frame)
        self.cc_fields_frame.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        for label, var_name in [("Credit Limit:", "credit_limit"),
                                ("Statement Close Day (1-31):", "statement_close_day"),
                                ("Payment Due Day (1-31):", "payment_due_day")]:
            ttk.Label(self.cc_fields_frame, text=label).grid(
                row=self.cc_fields_frame.grid_size()[1], column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar()
            ttk.Entry(self.cc_fields_frame, textvariable=var, width=30).grid(
                row=self.cc_fields_frame.grid_size()[1] - 1, column=1, padx=4, pady=2)
            self.form_vars[var_name] = var

        # Initially hide CC fields
        self.cc_fields_frame.grid_remove()

        # Form buttons
        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=SPACING["sm"])
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self._hide_form).pack(side=tk.LEFT, padx=4)

        self._editing_id = None

    def _on_type_change(self, event=None):
        if self.form_vars["type"].get() == "credit_card":
            self.cc_fields_frame.grid()
        else:
            self.cc_fields_frame.grid_remove()

    def _show_add_form(self):
        self._editing_id = None
        self.form_frame.configure(text="Add Account")
        for var in self.form_vars.values():
            var.set("")
        self.form_vars["type"].set("checking")
        self.form_vars["starting_balance"].set("0")
        self.cc_fields_frame.grid_remove()
        self.form_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

    def _edit_selected(self):
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an account to edit.")
            return

        item = self.table.tree.item(selected[0])
        name = item["values"][0]
        accts = self.account_repo.get_all()
        acct = next((a for a in accts if a.name == name), None)
        if not acct:
            return

        self._editing_id = acct.id
        self.form_frame.configure(text="Edit Account")
        self.form_vars["name"].set(acct.name)
        self.form_vars["type"].set(acct.type)
        self.form_vars["starting_balance"].set(str(acct.starting_balance))
        self.form_vars["credit_limit"].set(str(acct.credit_limit or ""))
        self.form_vars["statement_close_day"].set(str(acct.statement_close_day or ""))
        self.form_vars["payment_due_day"].set(str(acct.payment_due_day or ""))
        self._on_type_change()
        self.form_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

    def _hide_form(self):
        self.form_frame.pack_forget()
        self._editing_id = None

    def _save(self):
        name = self.form_vars["name"].get().strip()
        acct_type = self.form_vars["type"].get()

        if not name:
            messagebox.showerror("Error", "Account name is required.")
            return

        try:
            starting_balance = float(self.form_vars["starting_balance"].get() or "0")
        except ValueError:
            messagebox.showerror("Error", "Starting balance must be a number.")
            return

        credit_limit = None
        statement_close_day = None
        payment_due_day = None

        if acct_type == "credit_card":
            if self.form_vars["credit_limit"].get():
                try:
                    credit_limit = float(self.form_vars["credit_limit"].get())
                except ValueError:
                    messagebox.showerror("Error", "Credit limit must be a number.")
                    return
            if self.form_vars["statement_close_day"].get():
                try:
                    statement_close_day = int(self.form_vars["statement_close_day"].get())
                    if not 1 <= statement_close_day <= 31:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Statement close day must be 1-31.")
                    return
            if self.form_vars["payment_due_day"].get():
                try:
                    payment_due_day = int(self.form_vars["payment_due_day"].get())
                    if not 1 <= payment_due_day <= 31:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Payment due day must be 1-31.")
                    return

        try:
            if self._editing_id:
                acct = self.account_repo.get_by_id(self._editing_id)
                acct.name = name
                acct.type = acct_type
                acct.starting_balance = starting_balance
                acct.credit_limit = credit_limit
                acct.statement_close_day = statement_close_day
                acct.payment_due_day = payment_due_day
                self.account_repo.update(acct)
            else:
                self.account_repo.create(Account(
                    name=name, type=acct_type, starting_balance=starting_balance,
                    credit_limit=credit_limit, statement_close_day=statement_close_day,
                    payment_due_day=payment_due_day,
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self._hide_form()
        self.refresh()
        if self.on_change:
            self.on_change()

    def _delete_selected(self):
        selected = self.table.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an account to delete.")
            return

        item = self.table.tree.item(selected[0])
        name = item["values"][0]

        if not messagebox.askyesno("Confirm Delete", f"Delete account '{name}'?\nThis cannot be undone."):
            return

        accts = self.account_repo.get_all()
        acct = next((a for a in accts if a.name == name), None)
        if acct:
            try:
                self.account_repo.delete(acct.id)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot delete: {e}")
                return
        self.refresh()
        if self.on_change:
            self.on_change()

    def refresh(self):
        self.table.clear()
        from src.database.repositories.transaction_repo import TransactionRepository
        txn_repo = TransactionRepository(self.conn)
        calc = BalanceCalculator(self.account_repo, txn_repo)
        balances = calc.get_all_balances()

        for acct in self.account_repo.get_all():
            balance = balances.get(acct.id, acct.starting_balance)
            self.table.insert_row(values=(
                acct.name,
                acct.type.replace("_", " ").title(),
                format_currency(balance),
                format_currency(acct.credit_limit) if acct.credit_limit else "",
                acct.statement_close_day or "",
                acct.payment_due_day or "",
            ))
