"""Tiny CLI entrypoint tying the package together. Not exercised by the
test suite directly, but present because real packages have one and an
agent should not be surprised by it."""

from __future__ import annotations

import sys

from src.inventory.checkout import OrderLine, compute_order_total
from src.inventory.pricing import format_cents_as_currency
from src.inventory.receipt import render_receipt


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or len(argv) % 2 != 0:
        print("usage: cli.py SKU QTY [SKU QTY ...]", file=sys.stderr)
        return 2
    lines = [
        OrderLine(sku=argv[i], quantity=int(argv[i + 1]))
        for i in range(0, len(argv), 2)
    ]
    print(render_receipt(lines))
    print(format_cents_as_currency(compute_order_total(lines)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
