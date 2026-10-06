#!/usr/bin/env python3
"""Stage 3: end-to-end agentic benchmark via the real `claude` CLI.

For each model, clones a fresh copy of the fixture repo, runs `claude -p`
against it pointed at the local Ollama server (via env vars set only in the
subprocess's own environment — never exported into this process or the
parent shell), and grades the result independently:

  - `python3 -m pytest -q` rerun from scratch: must be exactly 5 passed,
    0 skipped, 0 xfail.
  - `git diff --name-only` must touch only files under src/.
  - Every file under tests/, plus conftest.py / pytest.ini / pyproject.toml
    if present, must be byte-identical (sha256) to the committed fixture.

3 runs per model. If the result is exactly 2/3, 2 more runs are added and
the gate re-evaluated on the 5-run rate, per the brief.

This Claude Code build (2.1.280) has no --max-turns flag (confirmed in
Phase 1 discovery both via --help and an empirical smoke test), so the
`timeout` wrapper is the only runaway-loop guard that actually exists here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger("e2e")

SETUP_DIR = Path.home() / "ollama-setup"
FIXTURE_TEMPLATE = SETUP_DIR / "fixtures" / "repo-template"
RUNS_DIR = SETUP_DIR / "fixtures" / "runs"
TRANSCRIPTS_DIR = SETUP_DIR / "transcripts"
RESULTS_JSONL = SETUP_DIR / "e2e_results.jsonl"

PROMPT = (
    "Run the test suite, find the bug, fix it, rerun until all tests pass. "
    "Do not modify files under tests/."
)

# Confirmed working empirically (Phase 1 discovery): variadic, space-separated.
ALLOWED_TOOLS = ["Read", "Edit", "Glob", "Grep", "Bash(python -m pytest:*)", "Bash(python3 -m pytest:*)", "Bash(pytest:*)"]

PROTECTED_NAMES = {"conftest.py", "pytest.ini", "pyproject.toml"}


class FixtureError(RuntimeError):
    pass


@dataclass
class E2ERunResult:
    model: str
    run_index: int
    host: str
    passed: bool = False
    tests_exit_ok: bool = False
    pytest_summary: str = ""
    only_src_touched: bool = False
    protected_files_identical: bool = False
    changed_files: list[str] = field(default_factory=list)
    wall_time_s: float = 0.0
    timed_out: bool = False
    exit_code: int | None = None
    error: str = ""
    transcript_path: str = ""
    max_single_request_input_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    turns: int = 0
    truncation_risk: bool = False


def make_checkout(model: str, run_index: int) -> Path:
    if not FIXTURE_TEMPLATE.exists():
        raise FixtureError(f"fixture template missing: {FIXTURE_TEMPLATE}")
    dest = RUNS_DIR / f"{model.replace(':', '_').replace('/', '_')}_{run_index}"
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "-q", str(FIXTURE_TEMPLATE), str(dest)], check=True)
    return dest


def pytest_check(repo: Path) -> tuple[bool, str]:
    r = subprocess.run(
        ["python3", "-m", "pytest", "-v", "--tb=no"], cwd=repo, capture_output=True, text=True
    )
    summary_lines = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l]
    summary = summary_lines[-1] if summary_lines else r.stdout[-500:]
    # Exact requirement: 5 passed, 0 skipped, 0 xfail.
    ok = r.returncode == 0 and "5 passed" in r.stdout and "skipped" not in r.stdout and "xfail" not in r.stdout
    return ok, summary


def diff_scope_check(repo: Path) -> tuple[bool, list[str]]:
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=repo, capture_output=True, text=True
    )
    changed = [line for line in r.stdout.splitlines() if line.strip()]
    r2 = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True
    )
    untracked_new = [
        line[3:] for line in r2.stdout.splitlines() if line.startswith("??")
    ]
    all_changed = changed + untracked_new
    only_src = all(f.startswith("src/") for f in all_changed) if all_changed else True
    return only_src, all_changed


def protected_files_check(repo: Path) -> bool:
    """Every file under tests/, plus conftest.py/pytest.ini/pyproject.toml
    at the repo root, must be byte-identical to the committed fixture."""
    ok = True
    for template_file in FIXTURE_TEMPLATE.rglob("*"):
        if template_file.is_dir():
            continue
        rel = template_file.relative_to(FIXTURE_TEMPLATE)
        is_protected = str(rel).startswith("tests/") or rel.name in PROTECTED_NAMES
        if not is_protected:
            continue
        candidate = repo / rel
        if not candidate.exists():
            log.warning("protected file missing in run: %s", rel)
            ok = False
            continue
        h1 = hashlib.sha256(template_file.read_bytes()).hexdigest()
        h2 = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if h1 != h2:
            log.warning("protected file MODIFIED: %s", rel)
            ok = False
    return ok


def parse_stream_json_metrics(transcript_path: Path) -> dict:
    """Best-effort extraction of token usage / turn count from
    --output-format stream-json output. If the format doesn't match what
    we expect, returns zeros rather than guessing."""
    max_input = 0
    total_in = 0
    total_out = 0
    turns = 0
    try:
        text = transcript_path.read_text(errors="ignore")
    except OSError:
        return {"max_single_request_input_tokens": 0, "total_input_tokens": 0, "total_output_tokens": 0, "turns": 0}

    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = d.get("message", {}).get("usage") or d.get("usage")
        if isinstance(usage, dict):
            inp = usage.get("input_tokens", 0) or 0
            out = usage.get("output_tokens", 0) or 0
            if inp or out:
                turns += 1
                total_in += inp
                total_out += out
                max_input = max(max_input, inp)
    return {
        "max_single_request_input_tokens": max_input,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "turns": turns,
    }


def run_once(model: str, run_index: int, host: str, num_ctx: int, timeout_s: int) -> E2ERunResult:
    result = E2ERunResult(model=model, run_index=run_index, host=host)
    try:
        repo = make_checkout(model, run_index)
    except (FixtureError, subprocess.CalledProcessError) as exc:
        result.error = f"fixture setup failed: {exc}"
        return result

    env_overrides = {
        "ANTHROPIC_BASE_URL": f"http://{host}",
        "ANTHROPIC_AUTH_TOKEN": "ollama",
        "ANTHROPIC_API_KEY": "",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
        "CLAUDE_CODE_SUBAGENT_MODEL": model,
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        # Confirmed via live CLI warning text in Phase 1 discovery — this is
        # the real, working lever for this Claude Code build, NOT the
        # CLAUDE_CODE_AUTO_COMPACT_WINDOW string found in ollama's binary
        # (that one is unverified for this Claude Code version).
        "CLAUDE_CODE_MAX_CONTEXT_TOKENS": str(num_ctx),
    }
    child_env = os.environ.copy()
    child_env.update(env_overrides)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    transcript_path = TRANSCRIPTS_DIR / f"{model.replace(':', '_').replace('/', '_')}_{run_index}.jsonl"
    result.transcript_path = str(transcript_path)

    cmd = [
        "claude", "-p", PROMPT,
        "--model", model,
        "--output-format", "stream-json",
        "--verbose",
        "--allowedTools", *ALLOWED_TOOLS,
    ]

    log.info("model=%s run=%d: launching claude in %s", model, run_index, repo)
    start = time.monotonic()
    try:
        with transcript_path.open("w") as tf:
            proc = subprocess.run(
                ["timeout", str(timeout_s), *cmd],
                cwd=repo, env=child_env, stdout=tf, stderr=subprocess.STDOUT,
            )
        result.exit_code = proc.returncode
        result.timed_out = proc.returncode == 124  # `timeout`'s own exit code for a kill
    except OSError as exc:
        result.error = f"failed to launch claude: {exc}"
        return result
    result.wall_time_s = time.monotonic() - start

    result.tests_exit_ok, result.pytest_summary = pytest_check(repo)
    result.only_src_touched, result.changed_files = diff_scope_check(repo)
    result.protected_files_identical = protected_files_check(repo)
    result.passed = (
        result.tests_exit_ok
        and result.only_src_touched
        and result.protected_files_identical
        and not result.timed_out
    )

    metrics = parse_stream_json_metrics(transcript_path)
    result.max_single_request_input_tokens = metrics["max_single_request_input_tokens"]
    result.total_input_tokens = metrics["total_input_tokens"]
    result.total_output_tokens = metrics["total_output_tokens"]
    result.turns = metrics["turns"]
    result.truncation_risk = result.max_single_request_input_tokens >= 0.9 * num_ctx

    log.info(
        "model=%s run=%d: tests_ok=%s scope_ok=%s protected_ok=%s timed_out=%s wall=%.1fs turns=%d -> %s",
        model, run_index, result.tests_exit_ok, result.only_src_touched,
        result.protected_files_identical, result.timed_out, result.wall_time_s,
        result.turns, "PASS" if result.passed else "FAIL",
    )
    if result.truncation_risk:
        log.warning(
            "model=%s run=%d: TRUNCATION RISK — max single-request input_tokens=%d >= 0.9*num_ctx(%d)",
            model, run_index, result.max_single_request_input_tokens, num_ctx,
        )
    return result


def append_result(r: E2ERunResult) -> None:
    with RESULTS_JSONL.open("a") as f:
        f.write(json.dumps(asdict(r)) + "\n")


def load_existing(model: str) -> list[dict]:
    if not RESULTS_JSONL.exists():
        return []
    out = []
    with RESULTS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("model") == model:
                out.append(d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1:11434")
    ap.add_argument("--models", nargs="+", required=True, help="ccb-<slug> Modelfile aliases")
    ap.add_argument("--num-ctx", type=int, default=65536)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    for model in args.models:
        existing = load_existing(model)
        done_indices = {d["run_index"] for d in existing}
        next_index = (max(done_indices) + 1) if done_indices else 1
        target_runs = 3

        runs = list(existing)
        for i in range(next_index, target_runs + 1):
            r = run_once(model, i, args.host, args.num_ctx, args.timeout)
            append_result(r)
            runs.append(asdict(r))

        pass_rate_3 = sum(1 for r in runs[:3] if r.get("passed")) / 3 if len(runs) >= 3 else None
        if pass_rate_3 is not None and abs(pass_rate_3 - 2 / 3) < 1e-9:
            log.info("model=%s: exactly 2/3, extending to 5 runs per the brief", model)
            for i in range(4, 6):
                if i in done_indices:
                    continue
                r = run_once(model, i, args.host, args.num_ctx, args.timeout)
                append_result(r)
                runs.append(asdict(r))

        final_n = len(runs)
        final_pass = sum(1 for r in runs if r.get("passed"))
        log.info("model=%s: e2e pass rate = %d/%d", model, final_pass, final_n)

    log.info("done. See %s and transcripts under %s", RESULTS_JSONL, TRANSCRIPTS_DIR)


if __name__ == "__main__":
    main()
