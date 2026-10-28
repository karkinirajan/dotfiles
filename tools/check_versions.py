#!/usr/bin/env python3
"""Version-drift checks against versions.yaml.

Offline (default, runs in CI on every push):
  * every ``<!-- v:key -->`` marker names a real key and equals versions.yaml
  * every entry has the required fields and a parseable version
  * every ``constraints`` rule holds
Live (``--live``, weekly job): compare entries with current Arch, CachyOS, AUR,
npm and PyPI data and report where a target is behind. Exit 1 only with
``--strict`` so a freshness report does not block unrelated work.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from _lib import LOG, MARKER_RE, load_versions, markdown_files, repo_root, setup_logging

REQUIRED = ("name", "target", "source")
SOURCES = {"arch", "cachyos", "aur", "upstream", "registry", "snapshot"}
OPS = {
    "==": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}


def vtuple(text: str, width: int | None = None) -> tuple[int, ...]:
    """Numeric prefix tuple of a version string ('1:0.57.0-1' -> (0, 57, 0))."""
    text = re.sub(r"^\d+:", "", str(text))
    nums = re.findall(r"\d+", re.split(r"[-+~_a-zA-Z]", text, maxsplit=1)[0] or text)
    parts = tuple(int(n) for n in nums)
    return parts[:width] if width else parts


def check_offline(root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entries: dict[str, dict[str, Any]] = data["entries"]
    for key, entry in entries.items():
        for field in REQUIRED:
            if field not in entry:
                errors.append(f"versions.yaml: {key}: missing '{field}'")
        if entry.get("source") not in SOURCES:
            errors.append(f"versions.yaml: {key}: source '{entry.get('source')}' not in {sorted(SOURCES)}")
        if "target" in entry and not vtuple(str(entry["target"])):
            errors.append(f"versions.yaml: {key}: target '{entry['target']}' has no numeric version")
        if "expect" in entry and "verify" not in entry:
            errors.append(f"versions.yaml: {key}: 'expect' without 'verify'")

    for md in markdown_files(root):
        if "docs/modernization/" in md.as_posix() and md.name not in ("HANDOFF.md",):
            continue
        text = md.read_text(encoding="utf-8")
        for match in MARKER_RE.finditer(text):
            key, field, current = match.group(1), match.group(2) or "target", match.group(3)
            entry = entries.get(key)
            rel = md.relative_to(root)
            if entry is None or field not in entry:
                errors.append(f"{rel}: marker '{key}:{field}' has no entry in versions.yaml")
            elif current != str(entry[field]):
                errors.append(f"{rel}: marker '{key}' reads '{current}', versions.yaml says '{entry[field]}'")

    for rule in data.get("constraints", []):
        rid = rule.get("id", "?")
        for req in rule.get("requires", []):
            entry = entries.get(req["key"])
            if entry is None:
                errors.append(f"constraint {rid}: unknown key '{req['key']}'")
                continue
            have = vtuple(str(entry[req.get("field", "target")]), req.get("width"))
            want = vtuple(str(req["value"]), req.get("width"))
            if req["op"] not in OPS or not OPS[req["op"]](have, want):
                errors.append(f"constraint {rid} violated: {req['key']} {have} {req['op']} {want} ({rule.get('text', '')})")
    return errors


def _json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "dotfiles-version-check/1.0"})
    with urllib.request.urlopen(req, timeout=40) as resp:  # noqa: S310 - fixed https hosts
        return json.load(resp)


def check_live(data: dict[str, Any]) -> list[str]:
    """Return human-readable drift notes (never raises on a network error)."""
    import pkg_lookup  # local import: needs zstandard only for this path

    notes: list[str] = []
    cachy = pkg_lookup.load_cachyos()
    for key, entry in data["entries"].items():
        target = str(entry["target"])
        hold = str(entry.get("hold", ""))
        try:
            if entry.get("npm"):
                latest = _json(f"https://registry.npmjs.org/{entry['npm']}/latest")["version"]
                _compare(notes, key, "npm", target, latest, hold)
            if entry.get("pypi"):
                latest = _json(f"https://pypi.org/pypi/{entry['pypi']}/json")["info"]["version"]
                _compare(notes, key, "pypi", target, latest, hold)
            pkg = entry.get("package")
            if pkg:
                for hit in pkg_lookup.arch_lookup(pkg):
                    _compare(notes, key, f"arch/{hit.source}", target, hit.version, hold)
                for hit in cachy.get(pkg, []):
                    _compare(notes, key, hit.source, target, hit.version, hold)
                if entry.get("source") == "aur":
                    for _name, hit in pkg_lookup.aur_lookup([pkg]).items():
                        _compare(notes, key, f"aur{' (flagged out-of-date)' if hit.note else ''}", target, hit.version, hold)
        except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
            notes.append(f"{key}: lookup failed ({exc})")
    return notes


def _compare(notes: list[str], key: str, where: str, target: str, found: str, hold: str = "") -> None:
    if where.endswith("testing"):
        return
    if vtuple(found) > vtuple(target):
        suffix = f" [hold: {hold}]" if hold else ""
        notes.append(f"{key}: target {target} is {'held behind' if hold else 'behind'} {where} {found}{suffix}")
    elif vtuple(found) < vtuple(target):
        notes.append(f"{key}: target {target} is ahead of {where} {found} (distro lag)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="compare with current repo/registry data (network)")
    ap.add_argument("--strict", action="store_true", help="with --live, exit 1 on any 'behind' note")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)
    root = repo_root()
    data = load_versions(root)

    errors = check_offline(root, data)
    for err in errors:
        LOG.error("DRIFT %s", err)
    LOG.info("%d entries, %d offline problems", len(data["entries"]), len(errors))
    status = 1 if errors else 0

    if args.live:
        notes = check_live(data)
        for note in notes:
            LOG.info("LIVE %s", note)
        behind = [n for n in notes if " is behind " in n or "lookup failed" in n]
        LOG.info("%d live notes, %d behind or failed", len(notes), len(behind))
        if args.strict and behind:
            status = 1
    return status


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
