#!/usr/bin/env python3
"""Repo style rules that tools can enforce.

* No em dashes in Markdown (owner rule for all written output).
* Chapter files carry valid frontmatter: title, topic, last_verified (ISO date),
  status, and optional ``versions`` keys that exist in versions.yaml.
* Fenced code blocks name a language (lint-friendly and renders consistently).
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
import sys
from pathlib import Path

from _lib import LOG, load_versions, markdown_files, repo_root, setup_logging, split_frontmatter

EM_DASH = "—"
ALLOWED_STATUS = {"current", "reference", "archived", "draft"}
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
# Generated or imported text that is not authored here.
STYLE_EXEMPT_PREFIXES = ("docs/modernization/inventory", "LICENSE")


def check_file(path: Path, root: Path, version_keys: set[str]) -> list[str]:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for lineno, line in enumerate(text.splitlines(), 1):
        if EM_DASH in line:
            errors.append(f"{rel}:{lineno}: em dash")

    in_fence: str | None = None
    for lineno, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if not m:
            continue
        marker = m.group(2)[0] * 3
        if in_fence is None:
            in_fence = marker
            if not m.group(3).strip():
                errors.append(f"{rel}:{lineno}: fenced block without a language")
        elif line.strip().startswith(in_fence):
            in_fence = None

    try:
        meta, _ = split_frontmatter(text)
    except ValueError as exc:
        return errors + [f"{rel}: {exc}"]
    if meta:
        for field in ("title", "topic", "last_verified", "status"):
            if field not in meta:
                errors.append(f"{rel}: frontmatter missing '{field}'")
        verified = meta.get("last_verified")
        if verified is not None:
            try:
                dt.date.fromisoformat(str(verified))
            except ValueError:
                errors.append(f"{rel}: last_verified '{verified}' is not an ISO date")
        if meta.get("status") not in ALLOWED_STATUS:
            errors.append(f"{rel}: status '{meta.get('status')}' not in {sorted(ALLOWED_STATUS)}")
        for key in meta.get("versions", []) or []:
            if key not in version_keys:
                errors.append(f"{rel}: frontmatter version key '{key}' not in versions.yaml")
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)
    root = repo_root()
    keys = set(load_versions(root)["entries"]) if (root / "versions.yaml").exists() else set()
    errors: list[str] = []
    count = 0
    for md in markdown_files(root):
        rel = md.relative_to(root).as_posix()
        if rel.startswith(STYLE_EXEMPT_PREFIXES):
            continue
        count += 1
        errors.extend(check_file(md, root, keys))
    for err in errors:
        LOG.error("STYLE %s", err)
    LOG.info("style-checked %d markdown files, %d problems", count, len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
