"""AlertBanner widget — colored banner for warnings/info with dismiss."""

import tkinter as tk
from tkinter import ttk

from src.ui.theme import FONTS


class AlertBanner(ttk.Frame):
    """A dismissible colored banner for displaying alerts."""

    def __init__(self, parent, message: str, alert_type: str = "warning", **kwargs):
        """Create an AlertBanner.

        Args:
            parent: Parent widget.
            message: Alert message text.
            alert_type: 'warning' (yellow), 'info' (blue), or 'error' (red).
        """
        super().__init__(parent, **kwargs)

        colors = {
            "warning": {"bg": "#FFF3CD", "fg": "#856404"},
            "info": {"bg": "#CCE5FF", "fg": "#004085"},
            "error": {"bg": "#F8D7DA", "fg": "#721C24"},
        }
        style = colors.get(alert_type, colors["info"])

        self.frame = tk.Frame(self, bg=style["bg"], padx=12, pady=8)
        self.frame.pack(fill=tk.X)

        label = tk.Label(
            self.frame, text=message, bg=style["bg"], fg=style["fg"],
            font=FONTS["body"], anchor="w", wraplength=900,
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        dismiss_btn = tk.Label(
            self.frame, text="x", bg=style["bg"], fg=style["fg"],
            font=FONTS["body"], cursor="hand2", padx=8,
        )
        dismiss_btn.pack(side=tk.RIGHT)
        dismiss_btn.bind("<Button-1>", lambda e: self.destroy())
