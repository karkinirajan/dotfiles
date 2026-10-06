"""Formats a human-readable receipt. No bug here; exists so the fixture is
more than a two-file toy and an agent has to navigate past irrelevant code
too."""

from __future__ import annotations

from src.inventory.catalog import find_product
from src.inventory.checkout import OrderLine, compute_order_total
from src.inventory.pricing import format_cents_as_currency


def render_receipt(lines: list[OrderLine]) -> str:
    rows = []
    for line in lines:
        product = find_product(line.sku)
        rows.append(f"{line.quantity}x {product.name} ({line.sku})")
    total = compute_order_total(lines)
    rows.append(f"TOTAL: {format_cents_as_currency(total)}")
    return "\n".join(rows)
