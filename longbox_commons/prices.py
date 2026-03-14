"""Price parsing utilities for comic marketplaces.

Handles currency symbols, commas, multiple decimal points, and other
non-numeric noise commonly found in scraped price strings.
"""

import re


def parse_price(price_text: str | None) -> float:
    """Parse a price string into a float value.

    Args:
        price_text: Raw price text (e.g. ``"$12.99"``, ``"1,299.00 USD"``).

    Returns:
        Parsed price as float, or ``0.0`` if unparseable/empty.
    """
    if not price_text:
        return 0.0

    price_str = re.sub(r"[^\d.]", "", price_text)

    if not price_str:
        return 0.0

    if price_str.count(".") > 1:
        parts = price_str.split(".")
        price_str = parts[0] + "." + parts[1]

    try:
        return float(price_str)
    except ValueError:
        return 0.0
