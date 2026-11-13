#!/usr/bin/env python3
"""Mutation check: apply deliberate bugs one at a time and require the test suite to fail for each.

Usage, from the repository root::

    python3 tests/mutation/mutate.py tests/mutation/mutants.py [name-filter ...] -- <test command ...>

The mutants file defines ``M = [(name, file, old, new), ...]``. Each ``old`` text must occur exactly once in its
file. The suite must pass unmutated first (a failing baseline would make every mutant look killed). A mutant counts
as killed when the suite then fails. Files are restored in a ``finally`` block, so do not kill a running check and
do not edit the tree while it runs. Exit status: 0 all killed, 1 a survivor or a bad pattern, 2 a failing baseline.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

TIMEOUT_SECONDS = 180
TIMED_OUT = 124


def load_mutants(spec: str) -> list[tuple[str, str, str, str]]:
    namespace: dict = {}
    exec(pathlib.Path(spec).read_text(encoding="utf-8"), namespace)
    return namespace["M"]


def run_suite(command: list[str], timeout: int | None = None) -> int:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return TIMED_OUT


def main(argv: list[str]) -> int:
    if "--" not in argv or not argv:
        print(__doc__)
        return 2
    split = argv.index("--")
    spec, filters, command = argv[0], argv[1:split], argv[split + 1:]
    mutants = load_mutants(spec)
    if filters:
        mutants = [m for m in mutants if any(word in m[0] for word in filters)]
    originals = {file: pathlib.Path(file).read_text(encoding="utf-8") for file in {m[1] for m in mutants}}

    baseline = subprocess.run(command, capture_output=True, text=True)
    if baseline.returncode:
        tail = "\n".join((baseline.stdout + baseline.stderr).splitlines()[-15:])
        print("BASELINE FAILS: the suite must pass before any mutation.\n" + tail)
        return 2
    print("baseline green", flush=True)

    problems: list[str] = []
    try:
        for name, file, old, new in mutants:
            count = originals[file].count(old)
            if count != 1:
                print(f"PATTERN? ({count}x) {name}", flush=True)
                problems.append(name)
                continue
            pathlib.Path(file).write_text(originals[file].replace(old, new), encoding="utf-8")
            killed = run_suite(command, TIMEOUT_SECONDS) != 0
            print(("killed   " if killed else "SURVIVED ") + name, flush=True)
            if not killed:
                problems.append(name)
            pathlib.Path(file).write_text(originals[file], encoding="utf-8")
    finally:
        for file, content in originals.items():
            pathlib.Path(file).write_text(content, encoding="utf-8")

    restored = all(pathlib.Path(f).read_text(encoding="utf-8") == c for f, c in originals.items())
    print(f"\n{len(mutants) - len(problems)}/{len(mutants)} killed; restored: {restored}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
