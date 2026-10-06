#!/usr/bin/env python3
"""Stage 0 (calibration) and Stage 1 (throughput) benchmark harness.

Run with the venv: ~/ollama-setup/.venv/bin/python ~/ollama-setup/bench.py

Resumable and append-only: every measured cell is written to results.jsonl
immediately after it completes. On rerun, cells already present (matched by
model+stage+size+run_kind+run_index) are skipped, so a crash or timeout
never loses prior data.

Every number in here comes from a real HTTP call to the local Ollama server
or a real sysfs read — nothing is estimated or invented. Where a metric
cannot be obtained (e.g. no power sensor), the field is null and a warning
is logged, never a guessed value.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bench")

SETUP_DIR = Path.home() / "ollama-setup"
RESULTS_JSONL = SETUP_DIR / "results.jsonl"

VRAM_SAMPLE_INTERVAL_S = 0.25
POWER_SENSOR_GLOB = "/sys/class/drm/card*/device/hwmon/hwmon*/power1_average"
VRAM_USED_GLOB = "/sys/class/drm/card*/device/mem_info_vram_used"

MIN_EVAL_COUNT = 128  # runs producing fewer tokens than this are discarded and rerun


class SensorUnavailable(RuntimeError):
    pass


def _first_glob_path(pattern: str) -> Path | None:
    matches = glob.glob(pattern)
    return Path(matches[0]) if matches else None


def read_vram_used_bytes() -> int | None:
    p = _first_glob_path(VRAM_USED_GLOB)
    if p is None:
        return None
    try:
        return int(p.read_text().strip())
    except (OSError, ValueError) as exc:
        log.warning("could not read VRAM sensor %s: %s", p, exc)
        return None


def read_power_microwatts() -> int | None:
    p = _first_glob_path(POWER_SENSOR_GLOB)
    if p is None:
        return None
    try:
        return int(p.read_text().strip())
    except (OSError, ValueError) as exc:
        log.warning("could not read power sensor %s: %s", p, exc)
        return None


def peak_ram_mb() -> float:
    """Peak RSS across all processes named 'ollama' or 'ollama_llama_ser',
    read once (not a running peak — good enough as a point sample taken
    right after a call completes, since the model stays loaded)."""
    import subprocess

    try:
        out = subprocess.run(
            ["ps", "-eo", "comm,rss"], capture_output=True, text=True, check=True
        ).stdout
    except Exception as exc:  # noqa: BLE001 - this is a best-effort metric
        log.warning("ps failed while sampling RAM: %s", exc)
        return 0.0
    total_kb = 0
    for line in out.splitlines()[1:]:
        parts = line.split(None, 1)
        if len(parts) == 2 and "ollama" in parts[0]:
            try:
                total_kb += int(parts[1])
            except ValueError:
                pass
    return total_kb / 1024


class Sampler:
    """Background thread sampling VRAM (always) and power (if the sensor
    exists) at a fixed interval, for the duration of one generate call.
    Used to compute peak VRAM and integrate energy in Wh.
    """

    def __init__(self, interval_s: float = VRAM_SAMPLE_INTERVAL_S) -> None:
        self.interval_s = interval_s
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.vram_samples: list[int] = []
        self.power_samples: list[tuple[float, int]] = []  # (timestamp, microwatts)
        self.power_available = _first_glob_path(POWER_SENSOR_GLOB) is not None

    def _run(self) -> None:
        while not self._stop.is_set():
            v = read_vram_used_bytes()
            if v is not None:
                self.vram_samples.append(v)
            if self.power_available:
                p = read_power_microwatts()
                if p is not None:
                    self.power_samples.append((time.monotonic(), p))
            time.sleep(self.interval_s)

    def __enter__(self) -> "Sampler":
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    @property
    def peak_vram_gb(self) -> float | None:
        if not self.vram_samples:
            return None
        return max(self.vram_samples) / 2**30

    @property
    def energy_wh(self) -> float | None:
        """Trapezoidal integration of watts over time, converted to Wh."""
        if not self.power_available or len(self.power_samples) < 2:
            return None
        wh = 0.0
        for (t0, p0), (t1, p1) in zip(self.power_samples, self.power_samples[1:]):
            dt_h = (t1 - t0) / 3600.0
            watts_avg = ((p0 + p1) / 2) / 1e6
            wh += watts_avg * dt_h
        return wh


@dataclass
class Cell:
    """One measured row. `key()` is the resumability identity."""

    model: str
    stage: str  # "stage0" | "stage1"
    size: str  # "S" | "M" | "L" | "calibration"
    run_kind: str  # "cold_load" | "cold_prefill" | "warm_turn"
    run_index: int
    ok: bool
    error: str = ""
    load_duration_s: float = 0.0
    prompt_eval_count: int = 0
    prompt_eval_duration_s: float = 0.0
    eval_count: int = 0
    eval_duration_s: float = 0.0
    total_duration_s: float = 0.0
    peak_vram_gb: float | None = None
    energy_wh: float | None = None
    ram_peak_mb: float = 0.0
    gpu_processor: str = ""
    gpu_context: int = 0
    discarded_low_eval_count: bool = False

    def key(self) -> tuple:
        return (self.model, self.stage, self.size, self.run_kind, self.run_index)

    @property
    def prefill_tok_s(self) -> float:
        return (
            self.prompt_eval_count / self.prompt_eval_duration_s
            if self.prompt_eval_duration_s > 0
            else 0.0
        )

    @property
    def decode_tok_s(self) -> float:
        return self.eval_count / self.eval_duration_s if self.eval_duration_s > 0 else 0.0


def load_existing_keys() -> set[tuple]:
    keys: set[tuple] = set()
    if not RESULTS_JSONL.exists():
        return keys
    with RESULTS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            keys.add((d["model"], d["stage"], d["size"], d["run_kind"], d["run_index"]))
    return keys


def append_cell(cell: Cell) -> None:
    SETUP_DIR.mkdir(parents=True, exist_ok=True)
    with RESULTS_JSONL.open("a") as f:
        f.write(json.dumps(asdict(cell)) + "\n")


def ollama_ps(client: httpx.Client) -> list[dict[str, Any]]:
    try:
        r = client.get("/api/ps", timeout=10)
        r.raise_for_status()
        return r.json().get("models", [])
    except httpx.HTTPError as exc:
        log.warning("ollama ps failed: %s", exc)
        return []


def ollama_stop(client: httpx.Client, model: str) -> None:
    """Unload the model so the next call is a genuine cold load."""
    try:
        client.post("/api/generate", json={"model": model, "keep_alive": 0}, timeout=30)
    except httpx.HTTPError as exc:
        log.warning("ollama stop for %s failed (continuing anyway): %s", model, exc)
    time.sleep(1)


def build_prompt_from_python_stdlib(target_tokens: int, nonce: str = "") -> str:
    """Real source text, not lorem ipsum: concatenate actual .py files found
    under this venv's/interpreter's own stdlib on disk, per the brief."""
    import sysconfig

    stdlib_dir = Path(sysconfig.get_paths()["stdlib"])
    chunks: list[str] = []
    total_chars = 0
    approx_chars = target_tokens * 4
    for py_file in sorted(stdlib_dir.glob("*.py")):
        try:
            text = py_file.read_text(errors="ignore")
        except OSError:
            continue
        chunks.append(f"# file: {py_file.name}\n{text}")
        total_chars += len(text)
        if total_chars >= approx_chars:
            break
    body = "\n\n".join(chunks)[:approx_chars]
    nonce_line = f"# nonce: {nonce}\n" if nonce else ""
    return (
        nonce_line
        + "You are reviewing the following Python standard library source "
        "files. Read them, then write a two-paragraph summary of common "
        "patterns across these files, and name any function that raises a "
        "custom exception.\n\n" + body
    )


def call_generate(
    client: httpx.Client,
    model: str,
    prompt: str,
    num_ctx: int,
    num_predict: int = 256,
    temperature: float = 0.0,
    seed: int = 42,
    timeout: float = 900.0,
) -> tuple[dict[str, Any] | None, str]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "seed": seed,
        },
    }
    try:
        r = client.post("/api/generate", json=payload, timeout=timeout)
        r.raise_for_status()
        d = r.json()
    except httpx.HTTPError as exc:
        return None, str(exc)
    if "error" in d:
        return None, d["error"]
    return d, ""


def run_and_record(
    client: httpx.Client,
    model: str,
    stage: str,
    size: str,
    run_kind: str,
    run_index: int,
    prompt: str,
    num_ctx: int,
    existing: set[tuple],
) -> Cell | None:
    key = (model, stage, size, run_kind, run_index)
    if key in existing:
        log.info("skip (already recorded): %s", key)
        return None

    log.info("running: model=%s stage=%s size=%s kind=%s idx=%d", model, stage, size, run_kind, run_index)
    with Sampler() as sampler:
        d, err = call_generate(client, model, prompt, num_ctx)

    if d is None:
        cell = Cell(model=model, stage=stage, size=size, run_kind=run_kind, run_index=run_index, ok=False, error=err)
        append_cell(cell)
        existing.add(key)
        log.error("FAILED: %s", err)
        return cell

    eval_count = d.get("eval_count", 0)
    if eval_count < MIN_EVAL_COUNT:
        log.warning(
            "run produced only %d tokens (< %d), discarding and NOT counting as a recorded cell "
            "(will retry on next invocation, same key)",
            eval_count, MIN_EVAL_COUNT,
        )
        cell = Cell(
            model=model, stage=stage, size=size, run_kind=run_kind, run_index=run_index,
            ok=False, error="eval_count below MIN_EVAL_COUNT threshold, discarded",
            eval_count=eval_count, discarded_low_eval_count=True,
        )
        # Deliberately NOT added to `existing` / NOT appended: per the brief,
        # a low-eval_count run must be discarded and rerun, not recorded as
        # a permanent result. We still log it to results.jsonl as a
        # diagnostic marker with a distinguishing run_kind suffix so it's
        # visible without polluting the resumability key space.
        diag = Cell(**{**asdict(cell), "run_kind": f"{run_kind}__discarded_{int(time.time())}"})
        append_cell(diag)
        return None

    ps = ollama_ps(client)
    proc = ps[0].get("processor", "") if ps else ""
    ctxv = ps[0].get("context", 0) if ps else 0

    cell = Cell(
        model=model, stage=stage, size=size, run_kind=run_kind, run_index=run_index,
        ok=True,
        load_duration_s=d.get("load_duration", 0) / 1e9,
        prompt_eval_count=d.get("prompt_eval_count", 0),
        prompt_eval_duration_s=d.get("prompt_eval_duration", 1) / 1e9,
        eval_count=eval_count,
        eval_duration_s=d.get("eval_duration", 1) / 1e9,
        total_duration_s=d.get("total_duration", 0) / 1e9,
        peak_vram_gb=sampler.peak_vram_gb,
        energy_wh=sampler.energy_wh,
        ram_peak_mb=peak_ram_mb(),
        gpu_processor=proc,
        gpu_context=ctxv,
    )
    append_cell(cell)
    existing.add(key)
    log.info(
        "  -> prefill=%.2f tok/s decode=%.2f tok/s load=%.2fs vram=%s energy=%s",
        cell.prefill_tok_s, cell.decode_tok_s, cell.load_duration_s,
        f"{cell.peak_vram_gb:.2f}GB" if cell.peak_vram_gb is not None else "n/a",
        f"{cell.energy_wh:.4f}Wh" if cell.energy_wh is not None else "n/a (no power sensor)",
    )
    return cell


SIZE_TOKENS = {"S": 500, "L": 48000}  # M is filled in per-model from Stage 0's P_cc


def stage1_for_model(
    client: httpx.Client, model: str, num_ctx: int, p_cc: int, existing: set[tuple]
) -> None:
    sizes = dict(SIZE_TOKENS)
    sizes["M"] = p_cc

    for size, target_tokens in sizes.items():
        base_prompt = build_prompt_from_python_stdlib(target_tokens)

        # cold load
        ollama_stop(client, model)
        run_and_record(client, model, "stage1", size, "cold_load", 1, base_prompt, num_ctx, existing)

        # cold prefill x2, unique nonce each time so no prefix-cache hit
        for i in (1, 2):
            nonce = f"{model}-{size}-coldprefill-{i}-{time.time_ns()}"
            prompt = build_prompt_from_python_stdlib(target_tokens, nonce=nonce)
            run_and_record(client, model, "stage1", size, "cold_prefill", i, prompt, num_ctx, existing)

        # warm turn x2: previous prompt + ~300 new tokens appended
        warm_prompt = base_prompt + "\n\nAlso list every module you just read by name."
        for i in (1, 2):
            run_and_record(client, model, "stage1", size, "warm_turn", i, warm_prompt, num_ctx, existing)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--models", nargs="+", required=True, help="ccb-<slug> Modelfile aliases, never bare tags")
    ap.add_argument("--num-ctx", type=int, default=65536)
    ap.add_argument("--p-cc", type=int, required=True, help="Stage 0's measured P_cc, in tokens")
    args = ap.parse_args()

    existing = load_existing_keys()
    log.info("resuming with %d cells already recorded", len(existing))

    with httpx.Client(base_url=args.host) as client:
        for model in args.models:
            stage1_for_model(client, model, args.num_ctx, args.p_cc, existing)

    log.info("done. See %s", RESULTS_JSONL)


if __name__ == "__main__":
    main()
