#!/bin/bash
# Restore Noctalia's settings.toml from the dotfiles repo, safely.
#
#   noctalia-restore.sh              restore the repo's current copy
#   noctalia-restore.sh <git-ref>    restore the copy from a commit or tag
#   noctalia-restore.sh --list       show the recent restore points
#
# Examples
#   noctalia-restore.sh                  # undo whatever Noctalia just did
#   noctalia-restore.sh HEAD~3           # three commits back
#   noctalia-restore.sh desktop-known-good
#
# Why this exists rather than just `cp`:
#
#   1. Noctalia must be STOPPED first. It keeps the whole config in memory and
#      writes it back out on its own schedule, so a file restored underneath a
#      running instance gets silently overwritten by the state you are trying
#      to replace.
#
#   2. The write has to be atomic. Noctalia watches this file and reloads on
#      every write; if it reads a half-written file it logs "no config files
#      found, using defaults" and then SAVES those defaults — which is exactly
#      how the config was destroyed on 2026-09-07.
#
#   3. It must restart as a plain child of Hyprland, not of whatever shell ran
#      this script. Apps launched from Noctalia's launcher inherit its cgroup,
#      and Chromium's sandbox crashes instantly inside a systemd service scope
#      (see noctalia-watchdog.sh). `hyprctl dispatch exec` gets that right.

set -uo pipefail

REPO="$HOME/dotfiles"
REL="wm/hyprland/noctalia/state/settings.toml"
LIVE="$HOME/.local/state/noctalia/settings.toml"
WATCHDOG="$HOME/.config/hypr/scripts/noctalia-watchdog.sh"
REF="${1:-}"

die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[2m  %s\033[0m\n' "$*"; }

if [ "$REF" = "--list" ]; then
    echo "Restore points touching the Noctalia config:"
    git -C "$REPO" log --oneline --decorate -15 -- "$REL"
    exit 0
fi

[ -d "$REPO/.git" ] || die "no dotfiles repo at $REPO"

# ── 1. Get the content we intend to install, and prove it is usable ──────────
STAGED="$(mktemp)"; trap 'rm -f "$STAGED"' EXIT
if [ -n "$REF" ]; then
    git -C "$REPO" show "$REF:$REL" > "$STAGED" 2>/dev/null \
        || die "cannot read $REL at ref '$REF'"
    SOURCE_DESC="$REF ($(git -C "$REPO" log -1 --format=%s "$REF" 2>/dev/null))"
else
    [ -f "$REPO/$REL" ] || die "missing $REPO/$REL"
    cp "$REPO/$REL" "$STAGED"
    SOURCE_DESC="repo working copy"
fi

python3 - "$STAGED" <<'PY' || die "the staged config is not valid TOML — refusing to install it"
import sys, tomllib, pathlib
d = tomllib.loads(pathlib.Path(sys.argv[1]).read_text())
bars = [b for b in d.get("bar", {}) if b != "order"]
anchor = d.get("shell", {}).get("panel_anchor_bar")
if not bars:
    print("refusing: no [bar.*] profile in the staged config", file=sys.stderr); sys.exit(1)
if anchor and anchor not in bars:
    # This exact mismatch silently breaks every panel and dropdown.
    print(f"refusing: shell.panel_anchor_bar={anchor!r} names no bar in {bars}", file=sys.stderr); sys.exit(1)
print(f"  validated: bar(s)={bars} widgets={len(d.get('widget', {}))} "
      f"plugins={len(d.get('plugins', {}).get('enabled', []))}")
PY

echo "restoring Noctalia config from: $SOURCE_DESC"

# ── 2. Stop Noctalia so it cannot write its in-memory state back ─────────────
pkill -f "bash $WATCHDOG" 2>/dev/null
pkill -x noctalia 2>/dev/null
for _ in $(seq 20); do pgrep -x noctalia >/dev/null || break; sleep 0.2; done
pgrep -x noctalia >/dev/null && die "Noctalia would not stop; aborting before writing"
info "stopped Noctalia and its watchdog"

# ── 3. Back up what is there, then install atomically ───────────────────────
if [ -f "$LIVE" ]; then
    cp -a "$LIVE" "$LIVE.bak-$(date +%Y%m%d-%H%M%S)"
    info "previous config saved next to it as settings.toml.bak-*"
fi
install -m 0644 "$STAGED" "$LIVE.tmp.$$" && mv -f "$LIVE.tmp.$$" "$LIVE"
info "wrote $LIVE"

# ── 4. Restart as a child of Hyprland, not of this shell ────────────────────
hyprctl dispatch exec "$WATCHDOG" >/dev/null 2>&1
for _ in $(seq 40); do pgrep -x noctalia >/dev/null && break; sleep 0.25; done
pgrep -x noctalia >/dev/null || die "Noctalia did not come back up — start $WATCHDOG by hand"
sleep 3

BAR=$(grep -oP '(?<=\[bar\] creating #0 ")[^"]+' "$HOME/.cache/noctalia/noctalia.log" 2>/dev/null | tail -1)
printf '\033[32mrestored\033[0m — Noctalia is back up with bar %s\n' "${BAR:-<unknown>}"
