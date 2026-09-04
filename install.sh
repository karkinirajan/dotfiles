#!/usr/bin/env bash
# =============================================================================
#  install.sh — link this repo's configs into their live locations.
#
#  The repo is the single source of truth. Every managed path becomes a symlink
#  back into the repo, so editing either side edits the same file and the two
#  can never drift apart.
#
#  Usage:
#    ./install.sh              link everything in manifest.conf
#    ./install.sh --dry-run    show what would happen, change nothing
#    ./install.sh status       report ok / drift / missing per entry
#    ./install.sh --force      replace a live symlink pointing somewhere else
#
#  Safe to re-run: already-correct links are left untouched. Any existing real
#  file is backed up to <path>.bak-<timestamp> before being replaced.
# =============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$REPO_DIR/manifest.conf"
TS="$(date +%Y%m%d-%H%M%S)"

DRY_RUN=0
FORCE=0
MODE="install"

for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN=1 ;;
    --force|-f)   FORCE=1 ;;
    status)       MODE="status" ;;
    -h|--help)    sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $arg (try --help)" >&2; exit 2 ;;
  esac
done

[ -f "$MANIFEST" ] || { echo "missing manifest: $MANIFEST" >&2; exit 1; }

# Counters
n_ok=0; n_linked=0; n_seeded=0; n_backed=0; n_skip=0; n_drift=0; n_missing=0; n_err=0

c_ok=$'\033[32m'; c_warn=$'\033[33m'; c_err=$'\033[31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
[ -t 1 ] || { c_ok=""; c_warn=""; c_err=""; c_dim=""; c_off=""; }

say() { printf '  %s%-6s%s %-44s %s\n' "$2" "$1" "$c_off" "$3" "${4:-}"; }

# Resolve a possibly-relative symlink target to an absolute path.
resolve() { ( cd "$(dirname "$1")" 2>/dev/null && readlink -f "$(basename "$1")" ) 2>/dev/null || true; }

do_link() {
  local src="$1" dst="$2"

  if [ ! -e "$src" ]; then
    say MISS "$c_err" "$dst" "repo path missing: $src"; n_err=$((n_err+1)); return
  fi

  # Already pointing at the right place — nothing to do.
  if [ -L "$dst" ] && [ "$(resolve "$dst")" = "$(readlink -f "$src")" ]; then
    [ "$MODE" = status ] && say ok "$c_ok" "$dst" || :
    n_ok=$((n_ok+1)); return
  fi

  if [ "$MODE" = status ]; then
    if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
      say MISS "$c_warn" "$dst" "not linked yet"; n_missing=$((n_missing+1))
    elif [ -L "$dst" ]; then
      say DRIFT "$c_warn" "$dst" "symlink -> $(readlink "$dst")"; n_drift=$((n_drift+1))
    elif diff -rq "$src" "$dst" >/dev/null 2>&1; then
      say COPY "$c_warn" "$dst" "real file, same content (not yet linked)"; n_drift=$((n_drift+1))
    else
      say DRIFT "$c_err" "$dst" "real file, CONTENT DIFFERS from repo"; n_drift=$((n_drift+1))
    fi
    return
  fi

  # A symlink somewhere else: only replace with --force.
  if [ -L "$dst" ] && [ "$FORCE" -ne 1 ]; then
    say SKIP "$c_warn" "$dst" "links elsewhere -> $(readlink "$dst") (use --force)"
    n_skip=$((n_skip+1)); return
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
      say PLAN "$c_dim" "$dst" "backup then link -> $src"
    else
      say PLAN "$c_dim" "$dst" "link -> $src"
    fi
    n_linked=$((n_linked+1)); return
  fi

  mkdir -p "$(dirname "$dst")"

  # Never destroy a real file without a copy of it.
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    mv "$dst" "$dst.bak-$TS"
    n_backed=$((n_backed+1))
    say BACKUP "$c_warn" "$dst" "-> $(basename "$dst").bak-$TS"
  fi

  rm -f "$dst"
  ln -s "$src" "$dst"
  say LINK "$c_ok" "$dst" "-> ${src#$REPO_DIR/}"
  n_linked=$((n_linked+1))
}

do_seed() {
  local src="$1" dst="$2"

  if [ ! -e "$src" ]; then
    say MISS "$c_err" "$dst" "repo path missing: $src"; n_err=$((n_err+1)); return
  fi

  if [ -e "$dst" ]; then
    [ "$MODE" = status ] && say ok "$c_ok" "$dst" "seeded (machine-owned, not tracked)" || :
    n_ok=$((n_ok+1)); return
  fi

  if [ "$MODE" = status ]; then
    say MISS "$c_warn" "$dst" "would be seeded"; n_missing=$((n_missing+1)); return
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    say PLAN "$c_dim" "$dst" "seed (copy) from ${src#$REPO_DIR/}"; n_seeded=$((n_seeded+1)); return
  fi

  mkdir -p "$(dirname "$dst")"
  cp -a "$src" "$dst"
  say SEED "$c_ok" "$dst" "copied from ${src#$REPO_DIR/}"
  n_seeded=$((n_seeded+1))
}

# ── Run ──────────────────────────────────────────────────────────────────────
case "$MODE" in
  status) echo "status — $REPO_DIR" ;;
  *) [ "$DRY_RUN" -eq 1 ] && echo "dry run — nothing will change" || echo "installing — $REPO_DIR" ;;
esac
echo

while read -r type src dst _rest; do
  [ -z "${type:-}" ] && continue
  case "$type" in \#*) continue ;; esac

  dst="${dst/#\~/$HOME}"
  src="$REPO_DIR/$src"

  case "$type" in
    link) do_link "$src" "$dst" ;;
    seed) do_seed "$src" "$dst" ;;
    *) echo "  ${c_err}bad type '$type'${c_off} in manifest" >&2; n_err=$((n_err+1)) ;;
  esac
done < <(grep -vE '^[[:space:]]*(#|$)' "$MANIFEST")

echo
if [ "$MODE" = status ]; then
  printf 'ok %d   drift %d   missing %d   error %d\n' "$n_ok" "$n_drift" "$n_missing" "$n_err"
  [ $((n_drift + n_missing + n_err)) -eq 0 ] && echo "everything is linked and in sync." \
                                             || echo "run ./install.sh to reconcile."
else
  printf 'linked %d   seeded %d   already-ok %d   backed-up %d   skipped %d   error %d\n' \
    "$n_linked" "$n_seeded" "$n_ok" "$n_backed" "$n_skip" "$n_err"
  [ "$n_backed" -gt 0 ] && echo "backups written with suffix .bak-$TS"
fi

exit $(( n_err > 0 ? 1 : 0 ))
