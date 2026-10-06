#!/usr/bin/env bash
# root-steps.sh — every privileged step for the Claude-Code-over-Ollama setup.
# I (the agent) never run sudo myself, per this task's hard rules. Run this
# YOURSELF, in a separate terminal, as:
#
#   sudo bash ~/ollama-setup/root-steps.sh
#
# Idempotent: safe to re-run. Every file it touches is backed up first with a
# timestamp suffix, and a rollback command is printed at the end.
#
# Batched to minimize how many times you have to run something as root: this
# covers Phase 2 Step 1 (Vulkan) AND the corrected Phase 3 server config in
# one pass, since ollama-vulkan and vulkan-radeon are already installed (no
# package step needed) and the two existing broken drop-ins need replacing
# either way. ROCm is NOT touched here — per this spec, it stays a deferred
# challenger, tested later only if Vulkan's Phase 5 Stage 1 numbers warrant
# it, and that will be a separate, small, one-line root-steps ask (a backend
# drop-in swap), not a package install (ollama-rocm is already present too).

set -euo pipefail

TS="$(date +%Y%m%d-%H%M%S)"
DROPIN_DIR="/etc/systemd/system/ollama.service.d"
OLLAMA_BIN="/usr/bin/ollama"
HOOK_FILE="/etc/pacman.d/hooks/ollama-setcap.hook"

log() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
backup() {
    local f="$1"
    if [ -f "$f" ]; then
        cp -a "$f" "${f}.bak.${TS}"
        log "backed up $f -> ${f}.bak.${TS}"
    fi
}

log "1/6: removing the two existing (broken) drop-ins, replacing with one consolidated file"
# Why replace rather than patch: Phase 1 discovery found override.conf's
# [Service] block had been overwritten at some point with a duplicate of
# context.conf's lines — its own header comment describes
# HSA_OVERRIDE_GFX_VERSION, but that line is gone from the actual config.
# Both old files ALSO set OLLAMA_CONTEXT_LENGTH globally, which this task's
# hard rules explicitly forbid (it would force a 64k KV cache onto every
# model including Continue.dev's, which shares this server). Context now
# lives only in per-model Modelfile `num_ctx`, set up in later phases.
backup "$DROPIN_DIR/override.conf"
backup "$DROPIN_DIR/context.conf"
mkdir -p "$DROPIN_DIR"

cat > "$DROPIN_DIR/claude-code.conf" <<'DROPIN'
# Managed by ~/ollama-setup/root-steps.sh — do not hand-edit; re-run that
# script (or its Phase-5/6 successor, if the backend choice changes) to
# change anything here. See ~/ollama-setup/REPORT.md for the measurements
# behind every value.
#
# Deliberately absent: OLLAMA_CONTEXT_LENGTH. Setting it here would apply a
# fixed context to EVERY model on this server, including whatever
# Continue.dev asks for. Context is set per-model via Modelfile `num_ctx`.
[Service]
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=30m"
# Phase 2 Step 1: Vulkan is the preferred backend, tried first. By default
# Ollama still SELECTS ROCm over Vulkan even with ollama-vulkan installed
# (confirmed empirically today: an unforced server picked
# library=ROCm compute=gfx1031; forcing OLLAMA_LLM_LIBRARY=vulkan was
# required to get library=Vulkan). This line is what actually makes Vulkan
# the live backend, not just an available one.
Environment="OLLAMA_LLM_LIBRARY=vulkan"
DROPIN
log "wrote $DROPIN_DIR/claude-code.conf"

rm -f "$DROPIN_DIR/override.conf" "$DROPIN_DIR/context.conf"
log "removed the two old drop-ins (backups above)"

log "2/6: setcap cap_perfmon+ep on the ollama binary"
# Why: lets Ollama's Vulkan backend query real free-VRAM from the kernel
# instead of guessing model-size-based approximations (per Ollama's own
# docs). There is one upstream report (ollama#15321) of this capability
# breaking GPU discovery on some setups — step 4 below verifies discovery
# still works, and step 6 tells you how to revert if it does not.
setcap cap_perfmon+ep "$OLLAMA_BIN"
getcap "$OLLAMA_BIN"

log "3/6: pacman hook to re-apply setcap after every ollama package upgrade"
# Why: pacman replaces the binary file wholesale on upgrade, which silently
# drops any capability set on the old file. Without this, Vulkan's
# free-VRAM reporting quietly degrades after the next `ollama` package
# update with no error, just worse scheduling decisions.
cat > "$HOOK_FILE" <<'HOOK'
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = ollama
Target = ollama-vulkan
Target = ollama-rocm

[Action]
Description = Re-applying cap_perfmon on /usr/bin/ollama after upgrade...
When = PostTransaction
Exec = /usr/sbin/setcap cap_perfmon+ep /usr/bin/ollama
HOOK
log "wrote $HOOK_FILE"

log "4/6: daemon-reload + restart"
systemctl daemon-reload
systemctl restart ollama
sleep 2
systemctl is-active --quiet ollama && log "ollama.service is active" || {
    echo "ollama.service failed to start — check: journalctl -u ollama -n 50" >&2
    exit 1
}

log "5/6: verify Vulkan discovery actually worked (this is what step 2's caveat asks for)"
sleep 3
if journalctl -u ollama --no-pager -n 60 2>&1 | grep -q 'library=Vulkan'; then
    log "CONFIRMED: library=Vulkan in the fresh service log"
else
    echo "WARNING: 'library=Vulkan' not seen yet in the last 60 log lines." >&2
    echo "This may just mean no model has loaded yet (GPU library selection logs" >&2
    echo "at model-load time, not at server-start time, in this Ollama version)." >&2
    echo "Load any model once (e.g. 'ollama run qwen3-coder:30b hi --verbose') and" >&2
    echo "re-check: journalctl -u ollama -n 60 | grep 'inference compute'" >&2
fi

log "6/6: effective environment now in use"
systemctl show ollama -p Environment

cat <<EOF

Rollback, if needed:
  sudo cp "$DROPIN_DIR/override.conf.bak.${TS}" "$DROPIN_DIR/override.conf"   # if it existed
  sudo cp "$DROPIN_DIR/context.conf.bak.${TS}"  "$DROPIN_DIR/context.conf"    # if it existed
  sudo rm -f "$DROPIN_DIR/claude-code.conf"
  sudo rm -f "$HOOK_FILE"
  sudo setcap -r "$OLLAMA_BIN"   # only if the cap_perfmon caveat (step 5) turns out to be a problem
  sudo systemctl daemon-reload && sudo systemctl restart ollama
EOF
