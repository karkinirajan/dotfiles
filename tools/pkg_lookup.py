#!/usr/bin/env python3
"""Resolve package names against Arch, CachyOS and AUR metadata.

Read-only. Used to keep the package manifests and ``versions.yaml`` honest:
every name is looked up in the official Arch repos (JSON API), the CachyOS
repos (repo databases on the mirror) and the AUR (RPC v5).

Usage:
    pkg_lookup.py --lists 01-system/cachyos/packages/*.txt -o out.csv
    pkg_lookup.py hyprland ollama-rocm paru
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import zstandard

LOG = logging.getLogger("pkg_lookup")
TIMEOUT = 60
USER_AGENT = "dotfiles-pkg-lookup/1.0 (+https://github.com/karkinirajan/dotfiles)"
ARCH_API = "https://archlinux.org/packages/search/json/"
AUR_RPC = "https://aur.archlinux.org/rpc/v5/info"
CACHYOS_MIRROR = "https://mirror.cachyos.org/repo"
# Repos the CachyOS installer enables on an x86-64-v3 machine, in pacman order.
CACHYOS_REPOS = (
    ("cachyos-v3", "x86_64_v3/cachyos-v3/cachyos-v3.db"),
    ("cachyos-core-v3", "x86_64_v3/cachyos-core-v3/cachyos-core-v3.db"),
    ("cachyos-extra-v3", "x86_64_v3/cachyos-extra-v3/cachyos-extra-v3.db"),
    ("cachyos", "x86_64/cachyos/cachyos.db"),
)
AUR_BATCH = 100


@dataclass(frozen=True)
class Hit:
    """One place a package name resolves."""

    source: str
    version: str
    updated: str = ""
    note: str = ""


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - fixed https hosts
        return resp.read()


def read_list(path: Path) -> Iterator[tuple[str, str]]:
    """Yield (name, declared_source) from a one-name-per-line package list."""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        yield parts[0], ("aur" if len(parts) > 1 and parts[1] == "(AUR)" else "repo")


def load_cachyos() -> dict[str, list[Hit]]:
    """Parse every enabled CachyOS repo database into name -> hits."""
    index: dict[str, list[Hit]] = {}
    for repo, rel in CACHYOS_REPOS:
        try:
            raw = _get(f"{CACHYOS_MIRROR}/{rel}")
        except urllib.error.URLError as exc:
            LOG.warning("cannot fetch %s: %s", repo, exc)
            continue
        data = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)).read()
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            for member in tar.getmembers():
                if not member.name.endswith("/desc"):
                    continue
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                fields = _parse_desc(extracted.read().decode("utf-8", "replace"))
                name = fields.get("NAME", "")
                if name:
                    index.setdefault(name, []).append(Hit(repo, fields.get("VERSION", "")))
        LOG.info("loaded %s", repo)
    return index


def _parse_desc(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    key = ""
    for line in text.splitlines():
        if line.startswith("%") and line.endswith("%"):
            key = line.strip("%")
        elif key and line and key not in out:
            out[key] = line
    return out


def arch_lookup(name: str) -> list[Hit]:
    """Query the official-repo JSON API for an exact package name."""
    url = f"{ARCH_API}?{urllib.parse.urlencode({'name': name})}"
    try:
        payload = json.loads(_get(url))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        LOG.warning("arch lookup failed for %s: %s", name, exc)
        return []
    return [
        Hit(r["repo"], f"{r['pkgver']}-{r['pkgrel']}", r["last_update"][:10])
        for r in payload.get("results", [])
    ]


def arch_provides(name: str) -> list[Hit]:
    """Find official packages that provide or replace ``name`` (renames)."""
    hits: list[Hit] = []
    for field in ("provides", "replaces"):
        url = f"{ARCH_API}?{urllib.parse.urlencode({field: name})}"
        try:
            payload = json.loads(_get(url))
        except (urllib.error.URLError, json.JSONDecodeError):
            continue
        hits.extend(
            Hit(r["repo"], f"{r['pkgver']}-{r['pkgrel']}", r["last_update"][:10], f"{field} {name}: {r['pkgname']}")
            for r in payload.get("results", [])
        )
    return hits


def aur_lookup(names: Iterable[str]) -> dict[str, Hit]:
    """Batch-query AUR RPC v5. Returns name -> Hit for names that exist."""
    found: dict[str, Hit] = {}
    pending = list(names)
    for i in range(0, len(pending), AUR_BATCH):
        chunk = pending[i : i + AUR_BATCH]
        query = "&".join(f"arg[]={urllib.parse.quote(n)}" for n in chunk)
        try:
            payload = json.loads(_get(f"{AUR_RPC}?{query}"))
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            LOG.warning("aur lookup failed: %s", exc)
            continue
        for r in payload.get("results", []):
            flag = "out-of-date" if r.get("OutOfDate") else ""
            found[r["Name"]] = Hit("aur", r["Version"], _date(r.get("LastModified")), flag)
    return found


def _date(epoch: int | None) -> str:
    if not epoch:
        return ""
    import datetime as dt

    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%d")


def resolve(entries: list[tuple[str, str]]) -> list[dict[str, str]]:
    """Resolve each (name, declared) against every source."""
    cachyos = load_cachyos()
    names = [n for n, _ in entries]
    aur = aur_lookup(names)
    rows: list[dict[str, str]] = []
    for name, declared in entries:
        hits = arch_lookup(name) + cachyos.get(name, [])
        if name in aur:
            hits.append(aur[name])
        note = ""
        provided_only = False
        if not hits:
            alt = arch_provides(name)
            if alt:
                note = "; ".join(h.note for h in alt[:3])
                hits = alt
                provided_only = True
        rows.append(
            {
                "package": name,
                "declared": declared,
                "found_in": " | ".join(f"{h.source}:{h.version}@{h.updated}" for h in hits[:5]),
                "status": "NAME-ABSENT-PROVIDED-BY-OTHER" if provided_only else _status(declared, hits),
                "note": note or "; ".join(h.note for h in hits if h.note and h.source == "aur"),
            }
        )
    return rows


def _status(declared: str, hits: list[Hit]) -> str:
    if not hits:
        return "MISSING"
    sources = {h.source for h in hits}
    in_repo = bool(sources - {"aur"})
    if declared == "aur" and in_repo:
        return "NOW-IN-REPO"
    if declared == "repo" and not in_repo:
        return "AUR-ONLY"
    if any(h.note == "out-of-date" for h in hits):
        return "OK-AUR-FLAGGED-OUT-OF-DATE"
    return "OK"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="package names to resolve")
    ap.add_argument("--lists", nargs="*", type=Path, default=[], help="package list files")
    ap.add_argument("-o", "--output", type=Path, help="write CSV here (default stdout)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s")

    entries: list[tuple[str, str]] = [(n, "repo") for n in args.names]
    for path in args.lists:
        entries.extend(read_list(path))
    if not entries:
        ap.error("give package names or --lists")
    seen: set[str] = set()
    entries = [e for e in entries if not (e[0] in seen or seen.add(e[0]))]

    rows = resolve(entries)
    out = args.output.open("w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=["package", "declared", "status", "found_in", "note"])
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if args.output:
            out.close()
    bad = [r for r in rows if r["status"] != "OK"]
    LOG.warning("%d packages, %d not plain OK", len(rows), len(bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
