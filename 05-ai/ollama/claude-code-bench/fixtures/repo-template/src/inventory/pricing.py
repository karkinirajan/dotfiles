"""Pricing and discount logic."""

from __future__ import annotations


def apply_bulk_discount(unit_price_cents: int, quantity: int) -> int:
    """Return the total price in cents for `quantity` units, with a 10%
    discount applied once quantity >= 5.
    """
    if quantity > 5:
        discounted_unit = round(unit_price_cents * 0.9)
        return discounted_unit * quantity
    return unit_price_cents * quantity


def format_cents_as_currency(cents: int) -> str:
    return f"${cents / 100:.2f}"
