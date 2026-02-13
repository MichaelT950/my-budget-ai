"""Reusable DataTable widget wrapping ttk.Treeview with scrollbars."""

import tkinter as tk
from tkinter import ttk


class DataTable(ttk.Frame):
    """A configurable table widget with scrollbars built on ttk.Treeview."""

    def __init__(self, parent, columns: list[tuple[str, str, int]], **kwargs):
        """Create a DataTable.

        Args:
            parent: Parent widget.
            columns: List of (column_id, heading_text, width) tuples.
        """
        super().__init__(parent, **kwargs)

        self.tree = ttk.Treeview(
            self,
            columns=[col[0] for col in columns],
            show="headings",
            selectmode="browse",
        )

        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, minwidth=50)

        # Alternating row colors
        self.tree.tag_configure("even_row", background="#F5F5F5")
        self.tree.tag_configure("odd_row", background="#FFFFFF")

        scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._row_count = 0

    def insert_row(self, values: tuple, tags: tuple = ()) -> str:
        """Insert a row at the end and return its item ID."""
        row_tag = "even_row" if self._row_count % 2 == 0 else "odd_row"
        all_tags = (row_tag,) + tags
        self._row_count += 1
        return self.tree.insert("", tk.END, values=values, tags=all_tags)

    def clear(self):
        """Remove all rows from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._row_count = 0

    def get_selected(self) -> dict | None:
        """Return values dict for selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        return dict(zip(columns, item["values"]))
