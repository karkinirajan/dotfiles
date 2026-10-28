#!/usr/bin/env python3
"""Check Markdown links: relative paths and anchors offline, URLs with --external.

Exit status 1 when any link is broken.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from _lib import LOG, markdown_files, repo_root, setup_logging, strip_code

INLINE_RE = re.compile(r"(?<!\!)\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
IMAGE_RE = re.compile(r"\!\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$", re.M)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)
HTML_ID_RE = re.compile(r"""<a\s+[^>]*?(?:id|name)=["']([^"']+)["']""", re.I)
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")
USER_AGENT = "dotfiles-link-check/1.0 (+https://github.com/karkinirajan/dotfiles)"
# Hosts that answer bots with 403/429 or need auth; a 401/403/429 there is not a broken link.
SOFT_HOSTS = ("linkedin.com", "medium.com", "x.com", "twitter.com", "support.upwork.com", "npmjs.com")


def slugify(heading: str) -> str:
    """GitHub-style heading slug."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def anchors_of(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    """All anchor ids a Markdown file exposes (slugs with -N dedupe plus HTML ids)."""
    if path in cache:
        return cache[path]
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_code(text)
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    for _, title in HEADING_RE.findall(body):
        slug = slugify(title)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    anchors.update(HTML_ID_RE.findall(text))
    cache[path] = anchors
    return anchors


def links_of(path: Path) -> list[str]:
    """Targets of every link and image in a Markdown file, code excluded."""
    text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
    found = INLINE_RE.findall(text) + IMAGE_RE.findall(text) + REFDEF_RE.findall(text) + AUTOLINK_RE.findall(text)
    return found


def check_local(src: Path, target: str, root: Path, cache: dict[Path, set[str]]) -> str | None:
    """Return an error string for a broken relative link, else None."""
    parsed = urllib.parse.urlsplit(target)
    rel = urllib.parse.unquote(parsed.path)
    frag = urllib.parse.unquote(parsed.fragment)
    dest = src if not rel else (root / rel.lstrip("/") if rel.startswith("/") else (src.parent / rel)).resolve()
    try:
        dest.relative_to(root.resolve())
    except ValueError:
        return f"escapes repo: {target}"
    if not dest.exists():
        return f"missing path: {target}"
    if frag and dest.is_file() and dest.suffix == ".md":
        if frag not in anchors_of(dest, cache):
            return f"missing anchor #{frag} in {dest.relative_to(root)}"
    return None


def check_url(url: str) -> str | None:
    """HEAD then GET a URL; return an error string if it is clearly broken."""
    host = urllib.parse.urlsplit(url).hostname or ""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:  # noqa: S310 - http(s) only, filtered by caller
                if resp.status < 400:
                    return None
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 405, 429) and (method == "HEAD" or any(h in host for h in SOFT_HOSTS)):
                if method == "HEAD" and exc.code in (405, 403):
                    continue
                return None
            if method == "GET" or exc.code not in (405, 501):
                return f"HTTP {exc.code}: {url}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if method == "GET":
                return f"unreachable ({exc}): {url}"
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--external", action="store_true", help="also check http(s) URLs (needs network)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)

    root = repo_root()
    cache: dict[Path, set[str]] = {}
    errors: list[str] = []
    urls: dict[str, list[str]] = {}
    for md in markdown_files(root):
        rel_md = md.relative_to(root)
        for target in links_of(md):
            if re.match(r"^(mailto:|tel:|data:|javascript:)", target):
                continue
            if re.match(r"^https?://", target):
                urls.setdefault(target.rstrip(".,;"), []).append(str(rel_md))
                continue
            if "{{" in target or "<" in target:
                continue
            problem = check_local(md, target, root, cache)
            if problem:
                errors.append(f"{rel_md}: {problem}")

    if args.external:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(check_url, u): u for u in urls}
            for fut in concurrent.futures.as_completed(futures):
                problem = fut.result()
                if problem:
                    url = futures[fut]
                    errors.append(f"{', '.join(sorted(set(urls[url])))}: {problem}")

    for line in sorted(errors):
        LOG.error("BROKEN %s", line)
    LOG.info("checked %d markdown files, %d external urls%s, %d broken",
             sum(1 for _ in markdown_files(root)), len(urls), "" if args.external else " (not fetched)", len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main())
