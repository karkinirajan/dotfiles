#!/usr/bin/env python3
"""Phase 6: if the Phase 5 winner spills to CPU, sweep Ollama's `num_gpu`
request option (layers to place on GPU) to see if more of the model can be
pushed onto the card without OOM, and re-measure decode tok/s at each step.

num_gpu is a per-request /api/generate option, not a server config — no
root needed, and no systemd restart between steps.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tune")

SETUP_DIR = Path.home() / "ollama-setup"
OUT = SETUP_DIR / "tune_results.json"

PROMPT = (
    "Write a Python function that merges two sorted lists into one sorted "
    "list without using the built-in sorted() function, then explain its "
    "time and space complexity in two sentences."
)


@dataclass
class TuneStep:
    num_gpu: int
    ok: bool
    error: str = ""
    decode_tok_s: float = 0.0
    vram_used_gb: float = 0.0


def vram_used_gb() -> float:
    for p in Path("/sys/class/drm").glob("card*/device/mem_info_vram_used"):
        try:
            return int(p.read_text().strip()) / 2**30
        except (OSError, ValueError):
            continue
    return 0.0


def try_num_gpu(host: str, model: str, num_gpu: int, num_ctx: int) -> TuneStep:
    payload = {
        "model": model,
        "prompt": PROMPT,
        "stream": False,
        "options": {"num_ctx": num_ctx, "num_gpu": num_gpu},
        "keep_alive": "0",  # force a fresh load each step so num_gpu actually re-applies
    }
    try:
        r = requests.post(f"http://{host}/api/generate", json=payload, timeout=300)
        r.raise_for_status()
        d = r.json()
    except requests.RequestException as exc:
        return TuneStep(num_gpu=num_gpu, ok=False, error=str(exc))
    if "error" in d:
        return TuneStep(num_gpu=num_gpu, ok=False, error=d["error"])
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1) / 1e9
    return TuneStep(
        num_gpu=num_gpu, ok=True,
        decode_tok_s=(ec / ed if ed > 0 else 0.0),
        vram_used_gb=vram_used_gb(),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1:11434")
    ap.add_argument("--model", required=True)
    ap.add_argument("--num-ctx", type=int, default=65536)
    ap.add_argument(
        "--values", type=int, nargs="+", default=[999, 60, 50, 40, 30, 20],
        help="num_gpu values to try, in order; 999 means 'as many as fit' (Ollama's own default-ish behavior)",
    )
    args = ap.parse_args()

    results: list[TuneStep] = []
    best: TuneStep | None = None
    for v in args.values:
        log.info("trying num_gpu=%d ...", v)
        step = try_num_gpu(args.host, args.model, v, args.num_ctx)
        results.append(step)
        if step.ok:
            log.info("  num_gpu=%d: OK decode=%.2f tok/s vram=%.2fGB", v, step.decode_tok_s, step.vram_used_gb)
            if best is None or step.decode_tok_s > best.decode_tok_s:
                best = step
        else:
            log.warning("  num_gpu=%d: FAILED: %s", v, step.error)

    OUT.write_text(json.dumps({"model": args.model, "steps": [asdict(s) for s in results]}, indent=2))
    if best:
        log.info("=== best: num_gpu=%d, %.2f tok/s ===", best.num_gpu, best.decode_tok_s)
    else:
        log.error("=== every num_gpu value failed ===")
    log.info("full results: %s", OUT)


if __name__ == "__main__":
    main()
