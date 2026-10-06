"""Product catalog: lookup and category grouping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    category: str
    unit_price_cents: int


CATALOG: dict[str, Product] = {
    "SKU-001": Product("SKU-001", "Widget", "hardware", 499),
    "SKU-002": Product("SKU-002", "Gadget", "hardware", 1299),
    "SKU-003": Product("SKU-003", "Gizmo", "electronics", 2599),
    "SKU-004": Product("SKU-004", "Sprocket", "hardware", 199),
}


def find_product(sku: str) -> Product:
    if sku not in CATALOG:
        raise KeyError(f"unknown sku: {sku}")
    return CATALOG[sku]


def products_in_category(category: str) -> list[Product]:
    return [p for p in CATALOG.values() if p.category == category]
