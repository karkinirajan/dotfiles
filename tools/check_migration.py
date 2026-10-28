#!/usr/bin/env python3
"""Confirm the migration map: every path tracked on the base branch still resolves.

A path passes when it exists in the working tree or is listed in
``docs/modernization/REMOVALS.md`` (a directory entry covers everything below it).
"""
from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys

from _lib import LOG, repo_root, setup_logging

DEFAULT_BASE = "origin/master"


def base_paths(root, base: str) -> list[str]:
    """Return the paths tracked on ``base``."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", base],
        check=True, capture_output=True, text=True,
    )
    return [p for p in out.stdout.splitlines() if p]


def removed_entries(root) -> tuple[set[str], list[str], bool]:
    """Return (exact removed paths, removed directory prefixes, bytecode removal listed)."""
    text = (root / "docs/modernization/REMOVALS.md").read_text(encoding="utf-8")
    exact: set[str] = set()
    prefixes: list[str] = []
    for token in re.findall(r"`([^`]+)`", text):
        if "/" not in token or " " in token:
            continue
        if token.endswith("/"):
            prefixes.append(token)
        else:
            exact.add(token)
    return exact, prefixes, "__pycache__" in text and ".pyc" in text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=DEFAULT_BASE, help="ref holding the pre-modernization tree")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)
    root = repo_root()
    try:
        paths = base_paths(root, args.base)
    except subprocess.CalledProcessError as exc:
        LOG.error("cannot read %s: %s", args.base, exc.stderr.strip())
        return 2
    exact, prefixes, bytecode_listed = removed_entries(root)
    lost: list[str] = []
    for path in paths:
        if (root / path).exists() or path in exact:
            continue
        if any(path.startswith(p) for p in prefixes):
            continue
        if bytecode_listed and "__pycache__/" in path and path.endswith(".pyc"):
            continue
        lost.append(path)
    for path in lost:
        LOG.error("UNRESOLVED %s: not on disk and not listed in REMOVALS.md", path)
    LOG.info("%d base paths checked, %d unresolved", len(paths), len(lost))
    return 1 if lost else 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
