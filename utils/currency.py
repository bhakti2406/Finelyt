EXCHANGE_RATES = {
    "INR": 1.0,
    "OMR": 0.0044,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
}

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "OMR": "OMR",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
}

def convert(amount_inr, to_currency="INR"):
    rate = EXCHANGE_RATES.get(to_currency, 1.0)
    return amount_inr * rate

def format_amount(amount_inr, currency="INR"):
    converted = convert(amount_inr, currency)
    symbol = CURRENCY_SYMBOLS.get(currency, "₹")
    if currency == "INR":
        return f"₹{converted:,.0f}"
    elif currency in ["USD", "EUR", "GBP"]:
        return f"{symbol}{converted:,.2f}"
    else:
        return f"{symbol} {converted:,.3f}"

def get_symbol(currency="INR"):
    return CURRENCY_SYMBOLS.get(currency, "₹")

def get_currencies():
    return list(EXCHANGE_RATES.keys())