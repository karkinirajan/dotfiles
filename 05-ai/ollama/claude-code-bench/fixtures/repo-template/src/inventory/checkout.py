"""Order checkout: ties catalog lookup and pricing together."""

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
