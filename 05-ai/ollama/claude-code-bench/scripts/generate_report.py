#!/usr/bin/env python3
"""Reads results.json, e2e_results.json, phase2_results.json and
tune_results.json (whichever exist) and produces the scored results table
for REPORT.md. Every number here is read straight from those files — this
script computes gates/ranking, it never fabricates a measurement.
"""

from __future__ import annotations

import json
import logging
import statistics
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("report")

SETUP_DIR = Path.home() / "ollama-setup"

GATE_DECODE = 10.0
GATE_TOOL = 0.8
GATE_E2E = 2.0 / 3.0


def load(path: Path) -> Any:
    if not path.exists():
        log.warning("missing: %s", path)
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        log.error("could not parse %s: %s", path, exc)
        return None


def main() -> None:
    bench = load(SETUP_DIR / "results.json") or {}
    e2e = load(SETUP_DIR / "e2e_results.json") or {}

    # bench.py nests results under a label; flatten to {model: data} using
    # the most recent label found (last key wins if run more than once).
    bench_flat: dict[str, dict] = {}
    for _label, models in bench.items():
        bench_flat.update(models)

    models = sorted(set(bench_flat) | set(e2e))
    rows = []
    for m in models:
        b = bench_flat.get(m, {})
        e_runs = e2e.get(m, [])
        decode = b.get("decode_tok_s_18k", 0.0)
        tool_rate = b.get("tool_pass_rate", 0.0)
        crashed = b.get("crashed", False)
        e2e_pass = sum(1 for r in e_runs if r.get("passed")) if e_runs else 0
        e2e_total = len(e_runs)
        e2e_rate = (e2e_pass / e2e_total) if e2e_total else 0.0
        e2e_times = [r["wall_time_s"] for r in e_runs if r.get("passed")]
        e2e_median = statistics.median(e2e_times) if e2e_times else None

        gate_decode_ok = decode >= GATE_DECODE
        gate_tool_ok = tool_rate >= GATE_TOOL
        gate_e2e_ok = e2e_rate >= GATE_E2E - 1e-9
        gate_crash_ok = not crashed
        all_gates = gate_decode_ok and gate_tool_ok and gate_e2e_ok and gate_crash_ok

        rows.append({
            "model": m,
            "decode_tok_s": decode,
            "gate_decode_ok": gate_decode_ok,
            "tool_pass_rate": tool_rate,
            "gate_tool_ok": gate_tool_ok,
            "e2e_pass": e2e_pass,
            "e2e_total": e2e_total,
            "e2e_rate": e2e_rate,
            "gate_e2e_ok": gate_e2e_ok,
            "e2e_median_wall_s": e2e_median,
            "crashed": crashed,
            "gate_crash_ok": gate_crash_ok,
            "all_gates_pass": all_gates,
        })

    passing = [r for r in rows if r["all_gates_pass"]]
    passing.sort(key=lambda r: (
        -r["e2e_rate"],
        r["e2e_median_wall_s"] if r["e2e_median_wall_s"] is not None else float("inf"),
        -r["tool_pass_rate"],
        -r["decode_tok_s"],
    ))

    fast_candidates = [r for r in passing if bench_flat.get(r["model"], {}).get("short_runs", [{}])]
    fast_pick = None
    for r in passing:
        procs = [
            run.get("gpu_processor", "")
            for run in bench_flat.get(r["model"], {}).get("long_runs", [])
        ]
        if procs and all(p == "100% GPU" for p in procs if p):
            fast_pick = r["model"]
            break

    out = {
        "rows": rows,
        "gates": {"decode_tok_s_min": GATE_DECODE, "tool_pass_rate_min": GATE_TOOL, "e2e_rate_min": GATE_E2E},
        "ranked_passing": [r["model"] for r in passing],
        "winner": passing[0]["model"] if passing else None,
        "fast_pick": fast_pick,
    }
    (SETUP_DIR / "scoring.json").write_text(json.dumps(out, indent=2))

    print(f"| Model | Decode tok/s (18k) | Tool acc | E2E pass | E2E median wall | Crashed | Gates |")
    print(f"|---|---|---|---|---|---|---|")
    for r in rows:
        gates = "PASS" if r["all_gates_pass"] else "fail"
        med = f"{r['e2e_median_wall_s']:.0f}s" if r["e2e_median_wall_s"] is not None else "n/a"
        print(
            f"| {r['model']} | {r['decode_tok_s']:.2f} "
            f"{'✓' if r['gate_decode_ok'] else '✗'} | "
            f"{r['tool_pass_rate']*100:.0f}% "
            f"{'✓' if r['gate_tool_ok'] else '✗'} | "
            f"{r['e2e_pass']}/{r['e2e_total']} "
            f"{'✓' if r['gate_e2e_ok'] else '✗'} | {med} | "
            f"{'yes' if r['crashed'] else 'no'} | {gates} |"
        )
    print()
    print(f"Winner (ranked, passing gates): {out['winner']}")
    print(f"Fast pick (100% GPU, passing gates): {out['fast_pick']}")
    if not passing:
        print("\nNO MODEL PASSED ALL GATES. Do not silently lower the gates — report this plainly.")


if __name__ == "__main__":
    main()
