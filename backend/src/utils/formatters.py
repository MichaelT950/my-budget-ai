"""Currency and display formatting utilities."""


def format_currency(amount: float) -> str:
    """Format a number as currency, e.g. 1234.5 -> '$1,234.50'."""
    return f"${amount:,.2f}"


def format_signed_currency(amount: float, transaction_type: str) -> str:
    """Format currency with +/- prefix based on transaction type.

    income -> +$amount, expense -> -$amount, transfer -> $amount (no prefix).
    """
    formatted = f"${abs(amount):,.2f}"
    if transaction_type == "income":
        return f"+{formatted}"
    elif transaction_type == "expense":
        return f"-{formatted}"
    return formatted
