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
#    ./install.sh pull         copy seeded files back live -> repo (see below)
#    ./install.sh restore      push seeded files repo -> live, overwriting
#    ./install.sh --force      replace a live symlink pointing somewhere else
#
#  Safe to re-run: already-correct links are left untouched. Any existing real
#  file is backed up to <path>.bak-<timestamp> before being replaced.
#
#  `link` entries can never drift — both paths are the same inode. `seed`
#  entries can: the owning program rewrites the live file and the repo copy
#  silently goes stale. `status` reports that drift, and the two directions are:
#
#    pull     live -> repo   capture what you changed, review it as a git diff
#    restore  repo -> live   put the repo's version back, overwriting live
#
#  `restore` is the recovery path when a program resets its own config. It
#  backs the live file up first. To go back to an OLDER state, check the file
#  out of git first, restore, then undo the checkout:
#
#    git checkout <commit> -- wm/hyprland/noctalia/state/settings.toml
#    ./install.sh restore
#    git checkout HEAD -- wm/hyprland/noctalia/state/settings.toml
#
#  For Noctalia specifically use wm/hyprland/hypr/scripts/noctalia-restore.sh,
#  which does the same thing but stops the shell first — restoring underneath a
#  running Noctalia lets it write its in-memory state back over the file.
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
    pull)         MODE="pull" ;;
    restore)      MODE="restore" ;;
    -h|--help)    awk 'NR>2{if (/^# ={10,}/) exit; print}' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $arg (try --help)" >&2; exit 2 ;;
  esac
done

[ -f "$MANIFEST" ] || { echo "missing manifest: $MANIFEST" >&2; exit 1; }

# Counters
n_ok=0; n_linked=0; n_seeded=0; n_backed=0; n_skip=0; n_drift=0; n_missing=0; n_err=0; n_pulled=0; n_restored=0

c_ok=$'\033[32m'; c_warn=$'\033[33m'; c_err=$'\033[31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
[ -t 1 ] || { c_ok=""; c_warn=""; c_err=""; c_dim=""; c_off=""; }

say() { printf '  %s%-6s%s %-44s %s\n' "$2" "$1" "$c_off" "$3" "${4:-}"; }

# Resolve a possibly-relative symlink target to an absolute path.
resolve() { ( cd "$(dirname "$1")" 2>/dev/null && readlink -f "$(basename "$1")" ) 2>/dev/null || true; }

do_link() {
  local src="$1" dst="$2"

  # A link entry is one file under two names — there is nothing to pull, and
  # nothing to restore either; re-linking is all "restore" can mean here.
  if [ "$MODE" = pull ]; then return; fi

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

  # Live file exists: repo and live are separate files, so compare them.
  if [ -e "$dst" ]; then
    if diff -rq "$src" "$dst" >/dev/null 2>&1; then
      { [ "$MODE" = status ] || [ "$MODE" = pull ]; } && say ok "$c_ok" "$dst" "seeded, in sync" || :
      n_ok=$((n_ok+1)); return
    fi

    if [ "$MODE" = pull ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        say PLAN "$c_dim" "$dst" "would pull live -> ${src#$REPO_DIR/}"; n_pulled=$((n_pulled+1)); return
      fi
      rm -rf "$src"; cp -a "$dst" "$src"
      say PULL "$c_ok" "$dst" "-> ${src#$REPO_DIR/} (review with git diff)"
      n_pulled=$((n_pulled+1)); return
    fi

    # restore: the opposite direction — the repo wins, live is overwritten.
    if [ "$MODE" = restore ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        say PLAN "$c_dim" "$dst" "would restore ${src#$REPO_DIR/} -> live"; n_restored=$((n_restored+1)); return
      fi
      mv "$dst" "$dst.bak-$TS"; n_backed=$((n_backed+1))
      cp -a "$src" "$dst"
      say RESTORE "$c_ok" "$dst" "<- ${src#$REPO_DIR/} (old saved as .bak-$TS)"
      n_restored=$((n_restored+1)); return
    fi

    # install/status: never clobber the live file the program owns.
    say DRIFT "$c_warn" "$dst" "live differs from repo copy (./install.sh pull)"
    n_drift=$((n_drift+1)); return
  fi

  if [ "$MODE" = pull ]; then
    say MISS "$c_warn" "$dst" "nothing live to pull"; n_missing=$((n_missing+1)); return
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
  pull)   echo "pull (live -> repo, seeded entries only) — $REPO_DIR" ;;
  restore) echo "restore (repo -> live, overwriting) — $REPO_DIR" ;;
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
if [ "$MODE" = pull ]; then
  printf 'pulled %d   already-ok %d   missing %d   error %d\n' "$n_pulled" "$n_ok" "$n_missing" "$n_err"
  [ "$n_pulled" -gt 0 ] && echo "review the changes with: git diff"
elif [ "$MODE" = restore ]; then
  printf 'restored %d   already-ok %d   linked %d   backed-up %d   error %d\n' \
    "$n_restored" "$n_ok" "$n_linked" "$n_backed" "$n_err"
  [ "$n_restored" -gt 0 ] && echo "restart the owning program so it reloads from disk"
elif [ "$MODE" = status ]; then
  printf 'ok %d   drift %d   missing %d   error %d\n' "$n_ok" "$n_drift" "$n_missing" "$n_err"
  [ $((n_drift + n_missing + n_err)) -eq 0 ] && echo "everything is linked and in sync." \
                                             || echo "run ./install.sh to reconcile."
else
  printf 'linked %d   seeded %d   already-ok %d   backed-up %d   skipped %d   error %d\n' \
    "$n_linked" "$n_seeded" "$n_ok" "$n_backed" "$n_skip" "$n_err"
  [ "$n_backed" -gt 0 ] && echo "backups written with suffix .bak-$TS"
fi

exit $(( n_err > 0 ? 1 : 0 ))
