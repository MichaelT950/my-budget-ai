"""Main application shell — sidebar nav, content area, view swapping."""

import tkinter as tk
from tkinter import ttk

from src.ui.theme import FONTS, SPACING, WINDOW_SIZE


class App(tk.Tk):
    """Main application window with sidebar navigation and content area."""

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.title("My Budget AI")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.minsize(800, 600)

        self._views: dict[str, ttk.Frame] = {}
        self._view_factories: dict[str, callable] = {}
        self._nav_buttons: dict[str, tk.Button] = {}
        self._current_view: str | None = None

        self._build_ui()

    def _build_ui(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main_frame, bg="#2C3E50", width=180)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # App title in sidebar
        tk.Label(
            self.sidebar, text="My Budget AI", bg="#2C3E50", fg="white",
            font=FONTS["subheading"], pady=SPACING["md"],
        ).pack(fill=tk.X)

        ttk.Separator(self.sidebar).pack(fill=tk.X, padx=8)

        self.nav_frame = tk.Frame(self.sidebar, bg="#2C3E50")
        self.nav_frame.pack(fill=tk.BOTH, expand=True, pady=SPACING["sm"])

        # Content area
        self.content = ttk.Frame(main_frame)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def register_view(self, name: str, factory: callable):
        """Register a view factory. Factory receives (parent, conn) and returns a Frame."""
        self._view_factories[name] = factory
        self._add_nav_button(name)

    def _add_nav_button(self, name: str):
        btn = tk.Button(
            self.nav_frame, text=name, bg="#2C3E50", fg="white",
            activebackground="#34495E", activeforeground="white",
            font=FONTS["body"], relief=tk.FLAT, anchor="w", padx=SPACING["md"],
            command=lambda: self.show_view(name),
        )
        btn.pack(fill=tk.X, pady=1)
        self._nav_buttons[name] = btn

    def show_view(self, name: str):
        if name not in self._view_factories:
            return

        # Highlight active nav button
        for btn_name, btn in self._nav_buttons.items():
            btn.configure(bg="#34495E" if btn_name == name else "#2C3E50")

        # Hide current view
        if self._current_view and self._current_view in self._views:
            self._views[self._current_view].pack_forget()

        # Create view if not yet instantiated
        if name not in self._views:
            view = self._view_factories[name](self.content, self.conn)
            self._views[name] = view

        # Show and refresh
        self._views[name].pack(fill=tk.BOTH, expand=True)
        if hasattr(self._views[name], "refresh"):
            self._views[name].refresh()
        self._current_view = name

    def _on_data_change(self):
        """Refresh the current view when data changes in another view."""
        if self._current_view and self._current_view in self._views:
            view = self._views[self._current_view]
            if hasattr(view, "refresh"):
                view.refresh()
