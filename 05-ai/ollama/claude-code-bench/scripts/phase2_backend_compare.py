#!/usr/bin/env python3
"""Phase 2: compare ROCm-spoofed, ROCm-native, and Vulkan on gemma4:12b.

Starts a fresh, isolated (non-root, user-owned) ollama serve instance for
each variant, on its own port, points it at the already-pulled test model
store, and runs a real generate call. Records whether the process crashed
(non-zero exit / process death / connection refused after start) and, if it
survived, the decode tok/s. Never touches the systemd-managed instance.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("phase2")

SETUP_DIR = Path.home() / "ollama-setup"
MODELS_DIR = SETUP_DIR / "test-models"
LOG_DIR = SETUP_DIR / "logs"
OUT = SETUP_DIR / "phase2_results.json"

MODEL = "gemma4:12b"
PROMPT = (
    "Write a Python function that merges two sorted lists into one sorted "
    "list without using the built-in sorted() function, then explain its "
    "time and space complexity in two sentences."
)


class BackendCrashed(RuntimeError):
    pass


@dataclass
class Variant:
    label: str
    port: int
    env: dict[str, str]


VARIANTS = [
    Variant("rocm_spoof_gfx1030", 11435, {"HSA_OVERRIDE_GFX_VERSION": "10.3.0"}),
    Variant("rocm_native_gfx1031", 11436, {}),
    Variant("vulkan", 11437, {"OLLAMA_LLM_LIBRARY": "vulkan"}),
]


@dataclass
class VariantResult:
    label: str
    port: int
    started_ok: bool = False
    gpu_line: str = ""
    library_detected: str = ""
    compute_detected: str = ""
    crashed: bool = False
    crash_detail: str = ""
    decode_tok_s: float = 0.0
    layers_offloaded: str = ""
    error: str = ""


def start_server(v: Variant) -> subprocess.Popen:
    env = os.environ.copy()
    env.update(v.env)
    env["OLLAMA_MODELS"] = str(MODELS_DIR)
    env["OLLAMA_HOST"] = f"127.0.0.1:{v.port}"
    env["OLLAMA_CONTEXT_LENGTH"] = "65536"
    env["OLLAMA_FLASH_ATTENTION"] = "1"
    env["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    env["OLLAMA_NUM_PARALLEL"] = "1"
    env["OLLAMA_MAX_LOADED_MODELS"] = "1"
    env["OLLAMA_KEEP_ALIVE"] = "2m"
    # explicitly clear any HSA override this shell already exports globally,
    # unless the variant wants it set above
    if "HSA_OVERRIDE_GFX_VERSION" not in v.env:
        env.pop("HSA_OVERRIDE_GFX_VERSION", None)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"phase2-{v.label}.log"
    log_f = open(log_path, "w")
    proc = subprocess.Popen(
        ["/usr/bin/ollama", "serve"], env=env, stdout=log_f, stderr=subprocess.STDOUT,
    )
    return proc


def wait_for_ready(port: int, timeout_s: int = 30) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/api/tags", timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def read_gpu_detection(log_path: Path) -> tuple[str, str]:
    """Return (library, compute) parsed from the server's own startup log."""
    text = log_path.read_text(errors="ignore")
    library = compute = ""
    for line in text.splitlines():
        if "inference compute" in line:
            for tok in line.split():
                if tok.startswith("library="):
                    library = tok.split("=", 1)[1]
                if tok.startswith("compute="):
                    compute = tok.split("=", 1)[1]
    return library, compute


def run_variant(v: Variant) -> VariantResult:
    result = VariantResult(label=v.label, port=v.port)
    log_path = LOG_DIR / f"phase2-{v.label}.log"
    log.info("=== variant %s (port %d) ===", v.label, v.port)
    proc = start_server(v)
    try:
        ready = wait_for_ready(v.port, timeout_s=30)
        if proc.poll() is not None:
            result.crashed = True
            result.crash_detail = f"process exited during startup, code={proc.returncode}"
            result.error = log_path.read_text(errors="ignore")[-2000:]
            log.error("%s: CRASHED on startup: %s", v.label, result.crash_detail)
            return result
        if not ready:
            result.crashed = True
            result.crash_detail = "server never responded on /api/tags within 30s"
            return result
        result.started_ok = True

        library, compute = read_gpu_detection(log_path)
        result.library_detected = library
        result.compute_detected = compute
        log.info("%s: detected library=%s compute=%s", v.label, library, compute)

        try:
            resp = requests.post(
                f"http://127.0.0.1:{v.port}/api/generate",
                json={"model": MODEL, "prompt": PROMPT, "stream": False,
                      "options": {"num_ctx": 65536}},
                timeout=300,
            )
            if proc.poll() is not None:
                result.crashed = True
                result.crash_detail = f"process died during generate, code={proc.returncode}"
                result.error = log_path.read_text(errors="ignore")[-2000:]
                log.error("%s: CRASHED during generate", v.label)
                return result
            resp.raise_for_status()
            d = resp.json()
            if "error" in d:
                result.error = d["error"]
                log.error("%s: generate returned error: %s", v.label, d["error"])
                return result
            eval_count = d.get("eval_count", 0)
            eval_dur = d.get("eval_duration", 1) / 1e9
            result.decode_tok_s = eval_count / eval_dur if eval_dur > 0 else 0.0
            log.info("%s: decode = %.2f tok/s (%d tokens / %.2fs)", v.label, result.decode_tok_s, eval_count, eval_dur)
        except requests.RequestException as exc:
            if proc.poll() is not None:
                result.crashed = True
                result.crash_detail = f"connection lost, process exited code={proc.returncode}: {exc}"
            else:
                result.error = str(exc)
            log.error("%s: request failed: %s", v.label, exc)
            return result

        text = log_path.read_text(errors="ignore")
        for line in text.splitlines():
            if "offloaded" in line and "layers to GPU" in line:
                result.layers_offloaded = line.strip().split("load_tensors:", 1)[-1].strip()

    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        time.sleep(2)  # let the port free up before the next variant

    return result


def main() -> None:
    results = []
    for v in VARIANTS:
        r = run_variant(v)
        results.append(asdict(r))
        OUT.write_text(json.dumps(results, indent=2))
    log.info("=== summary ===")
    for r in results:
        status = "CRASHED: " + r["crash_detail"] if r["crashed"] else (
            "OK" if r["started_ok"] and not r["error"] else f"ERROR: {r['error']}"
        )
        log.info(
            "%-22s compute=%-10s decode=%.2f tok/s  %s",
            r["label"], r["compute_detected"], r["decode_tok_s"], status,
        )
    log.info("full results: %s", OUT)


if __name__ == "__main__":
    main()
