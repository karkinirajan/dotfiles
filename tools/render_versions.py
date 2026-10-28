#!/usr/bin/env python3
"""Rewrite ``<!-- v:key -->text<!-- /v -->`` markers from versions.yaml.

Markers keep the version visible on GitHub while versions.yaml stays the only
place a version is written by hand. ``<!-- v:key:field -->`` selects another
field (``upstream``, ``arch``, ``cachyos``, ``aur``); the default is ``target``.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from _lib import LOG, MARKER_RE, load_versions, markdown_files, repo_root, setup_logging


def resolve(entries: dict, key: str, field: str | None) -> str:
    """Return the replacement text for a marker, raising KeyError when absent."""
    entry = entries[key]
    value = entry[field or "target"]
    return str(value)


def render(path: Path, entries: dict, write: bool) -> list[str]:
    """Return a list of problems; rewrite the file when ``write`` is true."""
    original = path.read_text(encoding="utf-8")
    problems: list[str] = []

    def repl(match) -> str:  # type: ignore[no-untyped-def]
        key, field, current = match.group(1), match.group(2), match.group(3)
        try:
            value = resolve(entries, key, field)
        except KeyError:
            problems.append(f"{path}: unknown version key or field '{key}{':' + field if field else ''}'")
            return match.group(0)
        if current != value:
            problems.append(f"{path}: marker '{key}' reads '{current}', versions.yaml says '{value}'")
        return f"<!-- v:{key}{':' + field if field else ''} -->{value}<!-- /v -->"

    updated = MARKER_RE.sub(repl, original)
    if write and updated != original:
        path.write_text(updated, encoding="utf-8")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report drift, change nothing")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)
    root = repo_root()
    entries = load_versions(root)["entries"]
    total = 0
    for md in markdown_files(root):
        if "docs/modernization/" in md.as_posix() and md.name != "HANDOFF.md":
            continue
        for problem in render(md, entries, write=not args.check):
            total += 1
            LOG.info("%s%s", "DRIFT " if args.check else "FIXED ", problem.replace(str(root) + "/", ""))
    return 1 if (args.check and total) else 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
