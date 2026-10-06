# inventory-fixture

Benchmark fixture: a small inventory/checkout package with one real,
cross-module logic bug. `pricing.py::apply_bulk_discount` has an off-by-one
on its discount threshold (`>` instead of `>=`). The failing tests live in
`checkout.py`'s domain (`test_order_total_five_units`) and directly in
`pricing.py`'s (`test_bulk_discount_at_exact_threshold`), but the fix
belongs only in `pricing.py`. 2 of 5 tests fail until it's fixed.

`tests/` must not be modified by the agent under benchmark — the grading
harness checks this independently (sha256 identity), not by trusting the
agent's own claim.
