# Deliberate bugs in the repo's checkers, one at a time: each (name, file, old text, new text) must make tools/tests fail.
# Run from the repository root (the driver checks the suite is green first; do not edit the tree while it runs; each `old` must occur exactly once):
#   uv run --with-requirements tools/requirements.txt --with pytest python tools/mutation/mutate.py tools/mutation/mutants.py -- \
#       uv run --with-requirements tools/requirements.txt --with pytest python -m pytest -x -q -p no:cacheprovider tools/tests
# (or, with a virtual environment that already has pyyaml, zstandard and pytest: replace the test command with `<venv>/bin/python -m pytest -x -q tools/tests`)
#
# Not listed, because they cannot change behaviour:
#  - _lib.py: the `inline` default of strip_code is exercised both ways; the fence marker `m.group(2)[0] * 3` in check_style.py (the same text for
#    the three-character fences the repo uses);
#  - _lib.py: the `\A` in FRONTMATTER_RE (it is used with `re.match`, which already anchors at the start of the text);
#  - gen_index.py: the `sorted(...)` in collect (`git ls-files -co` already returns paths in sorted order; the sort is kept so the output does
#    not depend on that);
#  - check_configs.py: `parser.optionxform = str` (it only keeps the case of keys, and the checker reads section names and nothing else);
#  - check_configs.py: the `and outside` guard on the comma in strip_jsonc (the lookahead already requires the characters after a comma to be
#    outside a string, and a comma inside a string is always followed by more string or the closing quote; the guard is kept to state the invariant);
#  - check_links.py: the `"<" in target` half of the template-placeholder skip (an angle-bracket target that is not an http link never reaches it).

L = "tools/_lib.py"
S = "tools/check_style.py"
K = "tools/check_links.py"
V = "tools/check_versions.py"
R = "tools/render_versions.py"
G = "tools/gen_index.py"
M_ = "tools/check_migration.py"
C = "tools/check_configs.py"

M = [
    # --- _lib
    ("lib: a non-mapping frontmatter is accepted", L, "    if not isinstance(meta, dict):\n", "    if False:\n"),
    ("lib: an impossible date escapes unwrapped", L, "except (yaml.YAMLError, ValueError) as exc:", "except yaml.YAMLError as exc:"),
    ("lib: versions.yaml without entries is accepted", L, 'if not isinstance(data, dict) or "entries" not in data:', "if not isinstance(data, dict):"),
    ("lib: tilde fences are not code", L, 'if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):', 'if fence is None and stripped.startswith("```"):'),
    ("lib: any fence closes any fence", L, "            if stripped.startswith(fence):\n", '            if stripped.startswith("```"):\n'),
    ("lib: inline code is always blanked", L, ") if inline else line)", ") if True else line)"),
    ("lib: untracked files are not listed", L, '"ls-files", "-co", "--exclude-standard"', '"ls-files", "-c", "--exclude-standard"'),
    ("lib: ignored files are listed", L, '"-co", "--exclude-standard"', '"-co"'),
    ("lib: a deleted tracked file is listed", L, "if (root / line).is_file()]", "if True]"),
    ("lib: version keys cannot contain dots", L, r"v:([A-Za-z0-9_.-]+)", r"v:([A-Za-z0-9_-]+)"),
    # --- check_style
    ("style: an en dash counts as an em dash", S, 'EM_DASH = "\\u2014"', 'EM_DASH = "\\u2013"'),
    ("style: nothing is exempt from the dash rule", S, "if EM_DASH in line and not rel.startswith(DASH_EXEMPT_PREFIXES):", "if EM_DASH in line:"),
    ("style: unlabelled fences are fine", S, "            if not m.group(3).strip():\n", "            if False:\n"),
    ("style: any fence-like line closes a block", S, "        elif line.strip().startswith(in_fence):\n", "        elif True:\n"),
    ("style: 'draft' is not a status", S, ', "draft"}', "}"),
    ("style: 'topic' is not required", S, '("title", "topic", "last_verified", "status")', '("title", "last_verified", "status")'),
    ("style: dates are not validated", S, "        if verified is not None:\n", "        if False:\n"),
    ("style: any status is fine", S, '        if meta.get("status") not in ALLOWED_STATUS:\n', "        if False:\n"),
    ("style: unknown version keys are fine", S, "            if key not in version_keys:\n", "            if False:\n"),
    ("style: agents' files are held to the frontmatter rule", S, '("/skills/", "/agents/", "/commands/")', '("/skills/", "/commands/")'),
    ("style: files without frontmatter must have it", S, "    if meta and not any(part in", "    if not any(part in"),
    ("style: the licence is checked", S, '"docs/modernization/inventory", "LICENSE", ', '"docs/modernization/inventory", '),
    ("style: problems do not fail the run", S, "    return 1 if errors else 0\n", "    return 0\n"),
    ("style: versions.yaml is required", S, 'keys = set(load_versions(root)["entries"]) if (root / "versions.yaml").exists() else set()', 'keys = set(load_versions(root)["entries"])'),
    # --- check_links
    ("links: underscores stay in slugs", K, 'text = re.sub(r"[`*_~]", "", text)', 'text = re.sub(r"[`*~]", "", text)'),
    ("links: slugs are ASCII only", K, 'text = re.sub(r"[^\\w\\- ]", "", text, flags=re.UNICODE)', 'text = re.sub(r"[^\\w\\- ]", "", text, flags=re.ASCII)'),
    ("links: spaces are dropped from slugs", K, 'return text.replace(" ", "-")', 'return text.replace(" ", "")'),
    ("links: repeated headings share an anchor", K, 'anchors.add(slug if count == 0 else f"{slug}-{count}")', "anchors.add(slug)"),
    ("links: html ids are not anchors", K, "    anchors.update(HTML_ID_RE.findall(text))\n", ""),
    ("links: anchors are not cached", K, "    if path in cache:\n", "    if False:\n"),
    ("links: headings in code are anchors", K, "body = strip_code(text, inline=False)", "body = text"),
    ("links: anchors are checked in non-markdown files", K, 'frag and dest.is_file() and dest.suffix == ".md" and frag', "frag and dest.is_file() and frag"),
    ("links: a missing path is fine", K, "    if not dest.exists():\n", "    if False:\n"),
    ("links: escaping the repo is fine", K, '        return f"escapes repo: {target}"\n', "        return None\n"),
    ("links: root-relative links resolve from the file", K, 'root / rel.lstrip("/") if rel.startswith("/") else', 'root / rel.lstrip("/") if False else'),
    ("links: paths are not decoded", K, "rel = urllib.parse.unquote(parsed.path)", "rel = parsed.path"),
    ("links: fragments are not decoded", K, "frag = urllib.parse.unquote(parsed.fragment)", "frag = parsed.fragment"),
    ("links: a second reference definition is swallowed", K, r"(?:[ \t]+.*)?$", r"(?:\s+.*)?$"),
    ("links: 429 is a broken link", K, "if exc.code in (401, 403, 405, 429) and", "if exc.code in (401, 403, 405) and"),
    ("links: a HEAD 403 is final", K, 'if method == "HEAD" and exc.code in (405, 403):', 'if method == "HEAD" and exc.code in (405,):'),
    ("links: a HEAD 501 is broken", K, 'if method == "GET" or exc.code not in (405, 501):', "if True:"),
    ("links: a HEAD connection error is final", K, '            if method == "GET":\n                return f"unreachable', '            if True:\n                return f"unreachable'),
    ("links: linkedin is checked like any host", K, 'SOFT_HOSTS = ("linkedin.com", ', "SOFT_HOSTS = ("),
    ("links: tel links are checked as files", K, r"^(mailto:|tel:|data:|javascript:)", r"^(mailto:|data:|javascript:)"),
    ("links: trailing punctuation stays in the url", K, 'urls.setdefault(target.rstrip(".,;"), [])', "urls.setdefault(target, [])"),
    ("links: urls are always fetched", K, "    if args.external:\n", "    if True:\n"),
    ("links: broken links do not fail the run", K, "    return 1 if errors else 0\n", "    return 0\n"),
    # --- check_versions
    ("versions: epochs are part of the version", V, 'text = re.sub(r"^\\d+:", "", str(text))', "text = str(text)"),
    ("versions: width is ignored", V, "return parts[:width] if width else parts", "return parts"),
    ("versions: 'name' is not required", V, 'REQUIRED = ("name", "target", "source")', 'REQUIRED = ("target", "source")'),
    ("versions: 'snapshot' is not a source", V, ', "snapshot"}', "}"),
    ("versions: any source is fine", V, '        if entry.get("source") not in SOURCES:\n', "        if False:\n"),
    ("versions: a non-numeric target is fine", V, '        if "target" in entry and not vtuple(str(entry["target"])):\n', "        if False:\n"),
    ("versions: expect without verify is fine", V, '        if "expect" in entry and "verify" not in entry:\n', "        if False:\n"),
    ("versions: modernization records are checked", V, '        if "docs/modernization/" in md.as_posix() and md.name not in ("HANDOFF.md",):\n', "        if False:\n"),
    ("versions: markers in code fences are fine", V, "            elif in_fence and MARKER_RE.search(line):\n", "            elif False:\n"),
    ("versions: a field marker reads the target", V, 'match.group(2) or "target", match.group(3)', '"target", match.group(3)'),
    ("versions: stale markers pass", V, "            elif current != str(entry[field]):\n", "            elif False:\n"),
    ("versions: >= is >", V, '">=": lambda a, b: a >= b,', '">=": lambda a, b: a > b,'),
    ("versions: <= is <", V, '"<=": lambda a, b: a <= b,', '"<=": lambda a, b: a < b,'),
    ("versions: == is !=", V, '"==": lambda a, b: a == b,', '"==": lambda a, b: a != b,'),
    ("versions: > is >=", V, '">": lambda a, b: a > b,', '">": lambda a, b: a >= b,'),
    ("versions: < is <=", V, '"<": lambda a, b: a < b,', '"<": lambda a, b: a <= b,'),
    ("versions: an unknown operator is a pass", V, 'if req["op"] not in OPS or not OPS[req["op"]](have, want):', 'if req["op"] in OPS and not OPS[req["op"]](have, want):'),
    ("versions: the rule's width is ignored on the target", V, 'have = vtuple(str(entry[field]), req.get("width"))', "have = vtuple(str(entry[field]))"),
    ("versions: the rule's width is ignored on the value", V, 'want = vtuple(str(req["value"]), req.get("width"))', 'want = vtuple(str(req["value"]))'),
    ("versions: a rule always reads the target", V, 'field = req.get("field", "target")', 'field = "target"'),
    ("versions: a missing rule field is not noticed", V, "            if field not in entry:\n                errors.append(f\"constraint", "            if False:\n                errors.append(f\"constraint"),
    ("versions: testing repositories are compared", V, '    if where.endswith("testing"):\n', "    if False:\n"),
    ("versions: equal versions are behind", V, "    if vtuple(found) > vtuple(target):\n", "    if vtuple(found) >= vtuple(target):\n"),
    ("versions: equal versions are ahead", V, "    elif vtuple(found) < vtuple(target):\n", "    elif vtuple(found) <= vtuple(target):\n"),
    ("versions: a hold is not labelled", V, "{'held behind' if hold else 'behind'}", "{'behind'}"),
    ("versions: strict ignores the behind filter", V, "        if args.strict and behind:\n", "        if args.strict and notes:\n"),
    ("versions: a failed lookup is not 'behind'", V, ' or "lookup failed" in n]', "]"),
    ("versions: --strict is always on", V, "        if args.strict and behind:\n", "        if behind:\n"),
    ("versions: drift does not fail the run", V, "    status = 1 if errors else 0\n", "    status = 0\n"),
    # --- render_versions
    ("render: a field marker reads the target", R, 'value = entry[field or "target"]', 'value = entry["target"]'),
    ("render: drift is not reported", R, "        if current != value:\n", "        if False:\n"),
    ("render: check mode writes", R, "    if write and updated != original:\n", "    if updated != original:\n"),
    ("render: an unknown key is blanked", R, "            return match.group(0)\n", '            return ""\n'),
    ("render: modernization records are rewritten", R, '        if "docs/modernization/" in md.as_posix() and md.name != "HANDOFF.md":\n', "        if False:\n"),
    ("render: drift does not fail check mode", R, "    return 1 if (args.check and total) else 0\n", "    return 0\n"),
    ("render: check mode is write mode", R, "write=not args.check", "write=True"),
    # --- gen_index
    ("index: docs are chapters", G, 'rel.parts[0] == "docs" or "references" in rel.parts', '"references" in rel.parts'),
    ("index: a reference folder is a chapter", G, ' or "reference" in rel.parts', ""),
    ("index: a title alone makes a chapter", G, 'if meta.get("title") and meta.get("topic"):', 'if meta.get("title"):'),
    ("index: the setup readme lists its own readme", G, 'rel.parent == base and rel.name != "README.md"', "rel.parent == base"),
    ("index: an empty setup guide is still written", G, "    if not mine:\n", "    if False:\n"),
    ("index: the setup readme is always written", G, "    if setup_readme is not None:\n", "    if True:\n"),
    ("index: a current file counts as stale", G, "        if current == content:\n", "        if False:\n"),
    ("index: check mode writes", G, "        if args.check:\n            LOG.error", "        if False:\n            LOG.error"),
    ("index: stale files do not fail check mode", G, "    return 1 if (args.check and stale) else 0\n", "    return 0\n"),
    # --- check_migration
    ("migration: a path with spaces is a path", M_, '        if " " in token:\n', "        if False:\n"),
    ("migration: a directory entry is an exact path", M_, '        if token.endswith("/"):\n', "        if False:\n"),
    ("migration: either word lists bytecode", M_, '"__pycache__" in text and ".pyc" in text', '"__pycache__" in text or ".pyc" in text'),
    ("migration: listed files are not recognised", M_, "if (root / path).exists() or path in exact:", "if (root / path).exists():"),
    ("migration: directory entries cover nothing", M_, "        if any(path.startswith(p) for p in prefixes):\n", "        if False:\n"),
    ("migration: bytecode is never skipped", M_, '        if bytecode_listed and "__pycache__/" in path and path.endswith(".pyc"):\n', "        if False:\n"),
    ("migration: lost paths do not fail the run", M_, "    return 1 if lost else 0\n", "    return 0\n"),
    ("migration: an unknown base is a plain failure", M_, '        LOG.error("cannot read %s: %s", args.base, exc.stderr.strip())\n        return 2\n', '        LOG.error("cannot read %s: %s", args.base, exc.stderr.strip())\n        return 1\n'),
    ("migration: a missing removals file passes", M_, "every removed path must be listed there\")\n        return 2\n", "every removed path must be listed there\")\n        return 0\n"),
    # --- check_configs
    ("configs: // comments are kept", C, '        elif text.startswith("//", i):\n', "        elif False:\n"),
    ("configs: /* */ comments are kept", C, '        elif text.startswith("/*", i):\n', "        elif False:\n"),
    ("configs: escapes are not honoured in strings", C, '            if ch == "\\\\" and i + 1 < n:\n', "            if False:\n"),
    ("configs: trailing commas before a newline stay", C, "            while nxt < len(out) and out[nxt][1] and out[nxt][0].isspace():\n", "            while False:\n"),
    ("configs: trailing commas before ] stay", C, 'out[nxt][0] in "}]":', 'out[nxt][0] in "}":'),
    ("configs: non-utf8 toml crashes", C, "except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:", "except tomllib.TOMLDecodeError as exc:"),
    ("configs: all json may have comments", C, "json.loads(strip_jsonc(text) if path.name in JSONC_FILES else text)", "json.loads(strip_jsonc(text))"),
    ("configs: only the first yaml document is read", C, "list(yaml.safe_load_all(path.read_text(encoding=\"utf-8\")))", "yaml.safe_load(path.read_text(encoding=\"utf-8\"))"),
    ("configs: a service needs no [Service]", C, '    if path.suffix == ".service" and not parser.has_section("Service"):\n', "    if False:\n"),
    ("configs: a timer needs no [Timer]", C, '    if path.suffix == ".timer" and not parser.has_section("Timer"):\n', "    if False:\n"),
    ("configs: duplicate unit keys are errors", C, "configparser.ConfigParser(strict=False,", "configparser.ConfigParser(strict=True,"),
    ("configs: a manifest row may have extra fields", C, "        if len(parts) != 3:\n", "        if len(parts) < 3:\n"),
    ("configs: any manifest type is fine", C, '        if kind not in ("link", "seed"):\n', "        if False:\n"),
    ("configs: a missing manifest source is fine", C, "        if not (root / src).exists():\n", "        if False:\n"),
    ("configs: a duplicate destination is fine", C, "        if dst in seen:\n", "        if False:\n"),
    ("configs: a missing manifest crashes", C, "    if not manifest.is_file():\n", "    if False:\n"),
    ("configs: '+' is not a package character", C, 'PKG_LINE = re.compile(r"^[a-z0-9@._+-]+(\\s+\\(AUR\\))?$")', 'PKG_LINE = re.compile(r"^[a-z0-9@._-]+(\\s+\\(AUR\\))?$")'),
    ("configs: duplicate packages are fine", C, "        if name in names:\n", "        if False:\n"),
    ("configs: units are checked everywhere", C, ' and "systemd" in rel.as_posix():', ":"),
    ("configs: host snapshots follow the list format", C, ' and "host-snapshot" not in rel.as_posix():', ":"),
    ("configs: problems do not fail the run", C, "    return 1 if errors else 0\n", "    return 0\n"),
]
