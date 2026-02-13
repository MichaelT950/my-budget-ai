"""Reports view — Cash Flow and Balance Sheet sub-tabs with charts."""

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from src.database.repositories.account_repo import AccountRepository
from src.database.repositories.category_repo import CategoryRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.services.balance_calculator import BalanceCalculator
from src.services.balance_sheet import BalanceSheetService
from src.services.cash_flow import CashFlowService
from src.ui.components.data_table import DataTable
from src.ui.theme import FONTS, SPACING
from src.utils.formatters import format_currency


class ReportsView(ttk.Frame):
    def __init__(self, parent, conn, **kwargs):
        super().__init__(parent, **kwargs)
        self.conn = conn
        self.account_repo = AccountRepository(conn)
        self.txn_repo = TransactionRepository(conn)
        self.category_repo = CategoryRepository(conn)
        self.balance_calc = BalanceCalculator(self.account_repo, self.txn_repo)
        self.cash_flow_svc = CashFlowService(self.txn_repo, self.category_repo)
        self.balance_sheet_svc = BalanceSheetService(self.account_repo, self.balance_calc)
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Reports", font=FONTS["heading"])
        title.pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        # Cash Flow tab
        self.cf_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cf_frame, text="Cash Flow")
        self._build_cash_flow_tab()

        # Balance Sheet tab
        self.bs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bs_frame, text="Balance Sheet")
        self._build_balance_sheet_tab()

    def _build_cash_flow_tab(self):
        # Period selector
        ctrl_frame = ttk.Frame(self.cf_frame)
        ctrl_frame.pack(fill=tk.X, padx=SPACING["sm"], pady=SPACING["sm"])

        ttk.Label(ctrl_frame, text="Period:", font=FONTS["body"]).pack(side=tk.LEFT, padx=4)
        self.cf_period_var = tk.StringVar(value="month")
        for text, val in [("Week", "week"), ("Month", "month"), ("Year", "year")]:
            ttk.Radiobutton(ctrl_frame, text=text, variable=self.cf_period_var, value=val,
                            command=self._refresh_cash_flow).pack(side=tk.LEFT, padx=4)

        # Summary
        self.cf_summary_frame = ttk.LabelFrame(self.cf_frame, text="Summary", padding=SPACING["sm"])
        self.cf_summary_frame.pack(fill=tk.X, padx=SPACING["sm"], pady=SPACING["sm"])

        # Chart area (matplotlib if available, otherwise text)
        self.cf_chart_frame = ttk.LabelFrame(self.cf_frame, text="Income vs Expenses", padding=SPACING["sm"])
        self.cf_chart_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        # Category breakdown table
        self.cf_cat_table = DataTable(self.cf_frame, columns=[
            ("category", "Category", 180),
            ("amount", "Amount", 120),
            ("percent", "% of Expenses", 120),
        ])
        self.cf_cat_table.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

    def _build_balance_sheet_tab(self):
        # Assets section
        self.bs_assets_frame = ttk.LabelFrame(self.bs_frame, text="Assets", padding=SPACING["sm"])
        self.bs_assets_frame.pack(fill=tk.X, padx=SPACING["sm"], pady=SPACING["sm"])

        # Liabilities section
        self.bs_liabilities_frame = ttk.LabelFrame(self.bs_frame, text="Liabilities", padding=SPACING["sm"])
        self.bs_liabilities_frame.pack(fill=tk.X, padx=SPACING["sm"], pady=SPACING["sm"])

        # Net worth
        self.bs_net_frame = ttk.LabelFrame(self.bs_frame, text="Net Worth", padding=SPACING["sm"])
        self.bs_net_frame.pack(fill=tk.X, padx=SPACING["sm"], pady=SPACING["sm"])

    def refresh(self):
        self._refresh_cash_flow()
        self._refresh_balance_sheet()

    def _get_period_dates(self) -> tuple[str, str]:
        today = date.today()
        period = self.cf_period_var.get()
        if period == "week":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif period == "year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        else:  # month
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start.isoformat(), end.isoformat()

    def _refresh_cash_flow(self):
        start, end = self._get_period_dates()
        result = self.cash_flow_svc.get_cash_flow(start, end)

        # Update summary
        for widget in self.cf_summary_frame.winfo_children():
            widget.destroy()

        items = [
            ("Total Income", format_currency(result.total_income), "#43A047"),
            ("Total Expenses", format_currency(result.total_expenses), "#E53935"),
            ("Net Cash Flow", format_currency(result.net_cash_flow),
             "#43A047" if result.net_cash_flow >= 0 else "#E53935"),
        ]
        for i, (label, value, color) in enumerate(items):
            frame = ttk.Frame(self.cf_summary_frame)
            frame.grid(row=0, column=i, padx=SPACING["md"], pady=SPACING["xs"])
            ttk.Label(frame, text=label, font=FONTS["small"]).pack()
            tk.Label(frame, text=value, font=FONTS["subheading"], fg=color).pack()

        # Update chart - try matplotlib, fall back to text
        for widget in self.cf_chart_frame.winfo_children():
            widget.destroy()

        try:
            self._render_cash_flow_chart(result)
        except Exception:
            # Fallback to text display
            if result.total_income > 0 or result.total_expenses > 0:
                bar_text = (
                    f"Income:   {'█' * max(1, int(result.total_income / max(result.total_income, result.total_expenses, 1) * 40))} "
                    f"{format_currency(result.total_income)}\n"
                    f"Expenses: {'█' * max(1, int(result.total_expenses / max(result.total_income, result.total_expenses, 1) * 40))} "
                    f"{format_currency(result.total_expenses)}"
                )
            else:
                bar_text = "No data for this period."
            tk.Label(self.cf_chart_frame, text=bar_text, font=FONTS["mono"],
                     justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=8, pady=8)

        # Update category breakdown
        self.cf_cat_table.clear()
        sorted_cats = sorted(result.expenses_by_category.items(), key=lambda x: x[1], reverse=True)
        for cat_name, amount in sorted_cats:
            pct = (amount / result.total_expenses * 100) if result.total_expenses > 0 else 0
            self.cf_cat_table.insert_row(values=(cat_name, format_currency(amount), f"{pct:.1f}%"))

    def _render_cash_flow_chart(self, result):
        """Render bar chart using matplotlib."""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        fig = Figure(figsize=(6, 3), dpi=80)
        ax = fig.add_subplot(111)

        categories_list = ["Income", "Expenses"]
        values = [result.total_income, result.total_expenses]
        colors = ["#43A047", "#E53935"]

        ax.bar(categories_list, values, color=colors, width=0.5)
        ax.set_ylabel("Amount ($)")
        ax.set_title(f"Period: {self.cf_period_var.get().title()}")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.cf_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _refresh_balance_sheet(self):
        result = self.balance_sheet_svc.get_balance_sheet()

        # Update assets
        for widget in self.bs_assets_frame.winfo_children():
            widget.destroy()
        for i, (name, balance) in enumerate(result.assets.items()):
            ttk.Label(self.bs_assets_frame, text=name, font=FONTS["body"]).grid(
                row=i, column=0, sticky="w", padx=4, pady=2)
            tk.Label(self.bs_assets_frame, text=format_currency(balance),
                     font=FONTS["body"], fg="#43A047").grid(row=i, column=1, sticky="e", padx=4, pady=2)
        ttk.Separator(self.bs_assets_frame, orient="horizontal").grid(
            row=len(result.assets), column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Label(self.bs_assets_frame, text="Total Assets", font=FONTS["subheading"]).grid(
            row=len(result.assets) + 1, column=0, sticky="w", padx=4)
        tk.Label(self.bs_assets_frame, text=format_currency(result.total_assets),
                 font=FONTS["subheading"], fg="#43A047").grid(
            row=len(result.assets) + 1, column=1, sticky="e", padx=4)

        # Update liabilities
        for widget in self.bs_liabilities_frame.winfo_children():
            widget.destroy()
        for i, (name, balance) in enumerate(result.liabilities.items()):
            ttk.Label(self.bs_liabilities_frame, text=name, font=FONTS["body"]).grid(
                row=i, column=0, sticky="w", padx=4, pady=2)
            tk.Label(self.bs_liabilities_frame, text=format_currency(balance),
                     font=FONTS["body"], fg="#E53935").grid(row=i, column=1, sticky="e", padx=4, pady=2)
        ttk.Separator(self.bs_liabilities_frame, orient="horizontal").grid(
            row=len(result.liabilities), column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Label(self.bs_liabilities_frame, text="Total Liabilities", font=FONTS["subheading"]).grid(
            row=len(result.liabilities) + 1, column=0, sticky="w", padx=4)
        tk.Label(self.bs_liabilities_frame, text=format_currency(result.total_liabilities),
                 font=FONTS["subheading"], fg="#E53935").grid(
            row=len(result.liabilities) + 1, column=1, sticky="e", padx=4)

        # Update net worth
        for widget in self.bs_net_frame.winfo_children():
            widget.destroy()
        color = "#43A047" if result.net_worth >= 0 else "#E53935"
        tk.Label(self.bs_net_frame, text=format_currency(result.net_worth),
                 font=("Helvetica", 24, "bold"), fg=color).pack(pady=SPACING["sm"])
