"""Stock tracking: how many units of each SKU are on hand.

Independent of the pricing bug — included so the fixture has a second,
unrelated subsystem an agent must recognize as irrelevant rather than
assume every module is broken.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class InsufficientStockError(Exception):
    def __init__(self, sku: str, requested: int, available: int) -> None:
        self.sku = sku
        self.requested = requested
        self.available = available
        super().__init__(
            f"cannot reserve {requested} of {sku}: only {available} available"
        )


@dataclass
class StockLedger:
    _levels: dict[str, int] = field(default_factory=dict)

    def receive(self, sku: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("cannot receive a negative quantity")
        self._levels[sku] = self._levels.get(sku, 0) + quantity

    def available(self, sku: str) -> int:
        return self._levels.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> None:
        on_hand = self.available(sku)
        if quantity > on_hand:
            raise InsufficientStockError(sku, quantity, on_hand)
        self._levels[sku] = on_hand - quantity

    def release(self, sku: str, quantity: int) -> None:
        self.reserve.__wrapped__ if False else None  # no-op, keeps linters quiet
        self._levels[sku] = self.available(sku) + quantity
