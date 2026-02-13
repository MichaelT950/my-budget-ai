"""Import CSV view — file picker, account selector, preview, confirm."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.services.categorizer import Categorizer
from src.services.importer import CsvImporter
from src.ui.components.data_table import DataTable
from src.ui.theme import FONTS, SPACING


class ImportCsvView(ttk.Frame):
    def __init__(self, parent, conn, on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.conn = conn
        self.account_repo = AccountRepository(conn)
        self.txn_repo = TransactionRepository(conn)
        self.category_repo = CategoryRepository(conn)
        self.on_change = on_change
        self._pending_result = None
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Import CSV", font=FONTS["heading"])
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        # Step 1: File selection
        file_frame = ttk.LabelFrame(self, text="Step 1: Select CSV File", padding=SPACING["sm"])
        file_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        self.file_var = tk.StringVar(value="No file selected")
        ttk.Label(file_frame, textvariable=self.file_var, font=FONTS["body"]).pack(side=tk.LEFT, padx=4)
        ttk.Button(file_frame, text="Browse...", command=self._browse_file).pack(side=tk.RIGHT, padx=4)

        # Step 2: Account selection
        acct_frame = ttk.LabelFrame(self, text="Step 2: Select Target Account", padding=SPACING["sm"])
        acct_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])

        self.acct_var = tk.StringVar()
        self.acct_combo = ttk.Combobox(acct_frame, textvariable=self.acct_var, state="readonly", width=40)
        self.acct_combo.pack(side=tk.LEFT, padx=4)
        ttk.Button(acct_frame, text="Preview", command=self._preview).pack(side=tk.RIGHT, padx=4)

        self._refresh_accounts()

        # Step 3: Preview
        preview_label = ttk.Label(self, text="Step 3: Preview (first 10 rows)", font=FONTS["subheading"])
        preview_label.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        self.preview_table = DataTable(self, columns=[
            ("date", "Date", 100),
            ("type", "Type", 80),
            ("amount", "Amount", 100),
            ("description", "Description", 250),
            ("category", "Auto Category", 140),
        ])
        self.preview_table.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        # Status and confirm
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, font=FONTS["body"]).pack(
            anchor="w", padx=SPACING["md"], pady=SPACING["xs"])

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["sm"])
        ttk.Button(btn_frame, text="Confirm Import", command=self._confirm_import).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=4)

    def _refresh_accounts(self):
        accounts = self.account_repo.get_all()
        self._accounts = accounts
        self.acct_combo["values"] = [f"{a.name} ({a.type.replace('_', ' ')})" for a in accounts]
        if accounts:
            self.acct_combo.current(0)

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def _preview(self):
        file_path = self.file_var.get()
        if file_path == "No file selected":
            messagebox.showwarning("No File", "Please select a CSV file first.")
            return

        if not self._accounts:
            messagebox.showwarning("No Accounts", "Please create an account first.")
            return

        acct_idx = self.acct_combo.current()
        if acct_idx < 0:
            messagebox.showwarning("No Account", "Please select a target account.")
            return

        account = self._accounts[acct_idx]
        importer = CsvImporter()
        result = importer.import_csv(file_path, account.id)
        self._pending_result = result

        # Auto-categorize for preview
        categories = self.category_repo.get_all()
        categorizer = Categorizer(categories)

        self.preview_table.clear()
        for txn in result.transactions[:10]:
            cat = categorizer.categorize_with_fallback(txn.description)
            txn.category_id = cat.id
            self.preview_table.insert_row(values=(
                txn.date, txn.type, f"${txn.amount:,.2f}", txn.description, cat.name,
            ))

        # Categorize remaining transactions too
        for txn in result.transactions[10:]:
            cat = categorizer.categorize_with_fallback(txn.description)
            txn.category_id = cat.id

        error_text = ""
        if result.errors:
            error_text = f" | {len(result.errors)} errors"
        self.status_var.set(
            f"Parsed {result.total_rows} rows: {len(result.transactions)} valid{error_text}"
        )

    def _confirm_import(self):
        if not self._pending_result or not self._pending_result.transactions:
            messagebox.showwarning("Nothing to Import", "Preview transactions first.")
            return

        txns = self._pending_result.transactions
        self.txn_repo.create_many(txns)

        count = len(txns)
        messagebox.showinfo("Import Complete", f"Successfully imported {count} transactions.")

        self._pending_result = None
        self.preview_table.clear()
        self.status_var.set("")
        self.file_var.set("No file selected")

        if self.on_change:
            self.on_change()

    def _cancel(self):
        self._pending_result = None
        self.preview_table.clear()
        self.status_var.set("")
        self.file_var.set("No file selected")

    def refresh(self):
        self._refresh_accounts()
