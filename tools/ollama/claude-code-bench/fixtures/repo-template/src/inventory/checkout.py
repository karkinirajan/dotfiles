"""Order checkout: ties catalog lookup and pricing together.

This is module A — where the bug's failing test lives — but the actual
defect is in pricing.apply_bulk_discount (module B). An agent that only
reads this file's traceback and "fixes" compute_order_total to hardcode a
different threshold would be patching the symptom, not the cause, and
would not generalize (a second test at a different quantity boundary would
still fail).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.inventory.catalog import find_product
from src.inventory.pricing import apply_bulk_discount


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int


def compute_order_total(lines: list[OrderLine]) -> int:
    total = 0
    for line in lines:
        product = find_product(line.sku)
        total += apply_bulk_discount(product.unit_price_cents, line.quantity)
    return total
