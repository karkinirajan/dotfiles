#!/usr/bin/env python3
"""Check that every mutant pattern matches exactly once in its file.

Run it after a session resume, after an interrupted mutation run, and after any reformat::

    python3 tests/mutation/check_patterns.py tests/mutation/mutants.py [more lists ...]

Python lists define ``M = [(name, file, old, new), ...]``. Node lists (``.mjs``) export a default array of
``{ name, file, old, new }`` objects and are read through ``node``.

A count of 0 means either that mutant is applied right now (the driver restores files only in its ``finally`` block, so
a killed run leaves one behind) or that the pattern went stale after an edit or a reformat. When the replacement text is
distinctive and present once, the line says "possibly APPLIED"; ``git diff -- <file>`` tells which it is. If it is an
applied mutant, swap ``new`` back to ``old`` in the file by hand, then re-run the suite.
Exit status: 0 all patterns match once, 1 a problem was found, 2 a list could not be read.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

# A replacement shorter than this proves nothing: "x" or "" can occur once in any file.
MIN_DISTINCTIVE = 12

NODE_DUMP = (
    "import(process.argv[1]).then(m => console.log(JSON.stringify(m.default.map("
    "({name, file, old, new: replacement}) => [name, file, old, replacement]))))"
)


def load(spec: str) -> list[tuple[str, str, str, str]]:
    path = pathlib.Path(spec).resolve()
    if path.suffix == ".mjs":
        out = subprocess.run(["node", "-e", NODE_DUMP, path.as_uri()], capture_output=True, text=True, check=True)
        return [tuple(item) for item in json.loads(out.stdout)]
    namespace: dict = {}
    exec(path.read_text(encoding="utf-8"), namespace)
    return namespace["M"]


def check(spec: str) -> int:
    problems = 0
    for name, file, old, new in load(spec):
        text = pathlib.Path(file).read_text(encoding="utf-8")
        count = text.count(old)
        if count == 1:
            continue
        problems += 1
        possibly_applied = count == 0 and len(new) >= MIN_DISTINCTIVE and text.count(new) == 1
        hint = "  <- possibly APPLIED (the replacement text is present once): check git diff" if possibly_applied else ""
        print(f"PATTERN? ({count}x) {name} [{file}]{hint}")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    total = 0
    for spec in argv:
        try:
            total += check(spec)
        except (OSError, subprocess.CalledProcessError, KeyError, SyntaxError, json.JSONDecodeError) as error:
            print(f"cannot read {spec}: {error}")
            return 2
    print("all patterns match once" if not total else f"{total} pattern problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
