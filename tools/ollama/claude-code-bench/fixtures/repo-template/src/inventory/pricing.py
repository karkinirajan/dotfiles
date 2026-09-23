"""Pricing and discount logic.

THE BUG lives here, in apply_bulk_discount, but its symptom only shows up
one layer up in checkout.compute_order_total (module A), because that is
the function whose test actually asserts a total price. Fixing checkout.py
would just be treating the symptom — the tests forbid touching anything
under tests/ but do not forbid an agent from "fixing" the wrong file; a
correct fix has to land here.
"""

from __future__ import annotations


def apply_bulk_discount(unit_price_cents: int, quantity: int) -> int:
    """Return the total price in cents for `quantity` units, with a 10%
    discount applied once quantity >= 5.

    BUG: the discount is applied to unit_price_cents BEFORE multiplying by
    quantity when quantity is large, but the threshold check uses `>` where
    it should use `>=`, AND the discount factor is applied per-unit only
    for the units *above* the threshold rather than the whole order. Net
    effect: ordering exactly 5 units gets no discount at all (off-by-one on
    the boundary), which is wrong per the stated 10%-at-5-or-more rule.
    """
    if quantity > 5:  # <-- bug: should be >= 5
        discounted_unit = round(unit_price_cents * 0.9)
        return discounted_unit * quantity
    return unit_price_cents * quantity


def format_cents_as_currency(cents: int) -> str:
    return f"${cents / 100:.2f}"
