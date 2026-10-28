#!/usr/bin/env python3
"""Parse-check the configuration files this repo ships.

Covers TOML, JSON/JSONC, YAML, systemd unit syntax, ``manifest.conf`` rows and
the package list format. A parse check proves the file is well formed, not
that the program accepts every key; key validity is tracked in the evidence
ledger.
"""
from __future__ import annotations

import argparse
import configparser
import json
import logging
import re
import sys
import tomllib
from pathlib import Path

import yaml
from _lib import LOG, repo_root, setup_logging, tracked_files

PKG_LINE = re.compile(r"^[a-z0-9@._+-]+(\s+\(AUR\))?$")
JSONC_FILES = {"vscode-settings.json", "vscode-keybindings.json", "settings.json", "sublime-settings.json",
               "anaconda-sublime.json", "sublime-repl.json", "vscode-extensions.json"}


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments and trailing commas outside of strings."""
    out: list[str] = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            out.append(ch)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 1
        else:
            out.append(ch)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def check_toml(path: Path) -> str | None:
    try:
        tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        return f"TOML: {exc}"
    return None


def check_json(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    try:
        json.loads(strip_jsonc(text) if path.name in JSONC_FILES else text)
    except json.JSONDecodeError as exc:
        return f"JSON: {exc}"
    return None


def check_yaml(path: Path) -> str | None:
    try:
        list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except yaml.YAMLError as exc:
        return f"YAML: {exc}"
    return None


def check_unit(path: Path) -> str | None:
    parser = configparser.ConfigParser(strict=False, interpolation=None, delimiters=("=",))
    parser.optionxform = str  # type: ignore[assignment,method-assign]
    try:
        parser.read_string(path.read_text(encoding="utf-8"))
    except configparser.Error as exc:
        return f"unit syntax: {exc}"
    if path.suffix == ".service" and not parser.has_section("Service"):
        return "service unit has no [Service] section"
    if path.suffix == ".timer" and not parser.has_section("Timer"):
        return "timer unit has no [Timer] section"
    return None


def check_manifest(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, int] = {}
    manifest = root / "manifest.conf"
    for lineno, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 3:
            errors.append(f"manifest.conf:{lineno}: expected '<type> <src> <dst>', got {len(parts)} fields")
            continue
        kind, src, dst = parts
        if kind not in ("link", "seed"):
            errors.append(f"manifest.conf:{lineno}: type '{kind}' is not link|seed")
        if not (root / src).exists():
            errors.append(f"manifest.conf:{lineno}: source missing: {src}")
        if dst in seen:
            errors.append(f"manifest.conf:{lineno}: destination {dst} already used at line {seen[dst]}")
        seen[dst] = lineno
    return errors


def check_package_list(path: Path) -> list[str]:
    errors: list[str] = []
    names: set[str] = set()
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not PKG_LINE.match(line):
            errors.append(f"{path.name}:{lineno}: not 'name' or 'name (AUR)': {line!r}")
            continue
        name = line.split()[0]
        if name in names:
            errors.append(f"{path.name}:{lineno}: duplicate package {name}")
        names.add(name)
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)
    root = repo_root()
    errors: list[str] = []
    checked = 0
    for path in tracked_files(root):
        rel = path.relative_to(root)
        problem: str | None = None
        if path.suffix == ".toml":
            problem = check_toml(path)
        elif path.suffix == ".json":
            problem = check_json(path)
        elif path.suffix in (".yaml", ".yml"):
            problem = check_yaml(path)
        elif path.suffix in (".service", ".timer", ".path", ".hook") and "systemd" in rel.as_posix():
            problem = check_unit(path)
        elif path.name.endswith(".txt") and "packages" in rel.as_posix() and "host-snapshot" not in rel.as_posix():
            errors.extend(f"{rel}: {e}" for e in check_package_list(path))
            checked += 1
            continue
        else:
            continue
        checked += 1
        if problem:
            errors.append(f"{rel}: {problem}")
    errors.extend(check_manifest(root))
    for err in errors:
        LOG.error("INVALID %s", err)
    LOG.info("parsed %d config files plus manifest.conf, %d problems", checked, len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
