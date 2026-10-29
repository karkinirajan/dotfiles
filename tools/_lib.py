"""Shared helpers for the repo checks in ``tools/``."""
from __future__ import annotations

import logging
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

LOG = logging.getLogger("tools")

# <!-- v:key --> text <!-- /v -->  or  <!-- v:key:field --> text <!-- /v -->
MARKER_RE = re.compile(r"<!--\s*v:([A-Za-z0-9_.-]+)(?::([a-z_]+))?\s*-->(.*?)<!--\s*/v\s*-->", re.S)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def setup_logging(verbose: bool = False) -> None:
    """Log bare messages to stdout so CI output stays readable."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )


def repo_root() -> Path:
    """Return the git top-level directory."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True
    )
    return Path(out.stdout.strip())


def tracked_files(root: Path, pattern: str | None = None) -> list[Path]:
    """Tracked plus untracked-not-ignored files, as absolute paths."""
    cmd = ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"]
    if pattern:
        cmd += ["--", pattern]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return [root / line for line in out.stdout.splitlines() if (root / line).is_file()]


def markdown_files(root: Path) -> Iterator[Path]:
    """Every Markdown file in the repo that is not generated session state."""
    yield from tracked_files(root, "*.md")


def load_versions(root: Path) -> dict[str, Any]:
    """Parse ``versions.yaml`` and return the mapping."""
    path = root / "versions.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict) or "entries" not in data:
        raise SystemExit(f"{path}: expected a mapping with an 'entries' key")
    return data


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter mapping, body). Empty mapping when absent."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid frontmatter: {exc}") from exc
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a mapping")
    return meta, text[match.end():]


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and inline code so regexes skip them."""
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            out.append("\n")
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            out.append("\n")
            continue
        out.append(re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line))
    return "".join(out)
