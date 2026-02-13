"""UI theme constants — colors, fonts, spacing, window dimensions."""

CATEGORY_COLORS = {
    "red": "#E53935",
    "orange": "#FB8C00",
    "yellow": "#FDD835",
    "green": "#43A047",
    "blue": "#1E88E5",
    "purple": "#8E24AA",
    "pink": "#D81B60",
    "gray": "#757575",
}

FONTS = {
    "heading": ("Helvetica", 18, "bold"),
    "subheading": ("Helvetica", 14, "bold"),
    "body": ("Helvetica", 12),
    "small": ("Helvetica", 10),
    "mono": ("Courier", 12),
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

WINDOW_SIZE = (1100, 750)

# Transaction type colors for display
TYPE_COLORS = {
    "income": "#43A047",   # green
    "expense": "#E53935",  # red
    "transfer": "#757575", # gray
}
