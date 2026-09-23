#!/usr/bin/env bash
# root-steps-backend-switch.sh — installs the /usr/local/sbin/ollama-backend
# helper (exactly as this task's spec describes) and uses it once, now, to
# switch to ROCm for testing.
#
# WHY THIS IS NEEDED NOW, out of the spec's original order: Stage 0
# calibration on Vulkan (the preferred backend from root-steps.sh) hit a
# real, reproduced crash — `ggml_vulkan: device lost on Vulkan0` — at the
# large prompt sizes Claude Code's real requests actually use (~25-33k
# tokens). Two identical reproductions, not a one-off. See STATE.md for the
# full journalctl evidence. The spec's "defer ROCm until Stage 1 has Vulkan
# numbers" was premised on Vulkan being usable at realistic sizes; it is
# not, as measured. This is not skipping ahead carelessly — it's the
# earliest point a real crash could have been discovered, and the helper
# below is exactly the mechanism the spec describes for this situation.
#
# Run as:  sudo bash ~/ollama-setup/root-steps-backend-switch.sh
#
# Idempotent, backs up before touching anything.

set -euo pipefail

TS="$(date +%Y%m%d-%H%M%S)"
DROPIN_DIR="/etc/systemd/system/ollama.service.d"
HELPER="/usr/local/sbin/ollama-backend"

log() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
backup() {
    local f="$1"
    [ -f "$f" ] && { cp -a "$f" "${f}.bak.${TS}"; log "backed up $f -> ${f}.bak.${TS}"; }
}

log "1/3: installing $HELPER"
mkdir -p /usr/local/sbin
cat > "$HELPER" <<'HELPEREOF'
#!/usr/bin/env bash
# ollama-backend {vulkan|rocm} — swaps the GPU-backend drop-in and restarts
# ollama. Managed by ~/ollama-setup; part of the Claude-Code-over-Ollama
# benchmark setup. Must be run as root.
set -euo pipefail
DROPIN_DIR="/etc/systemd/system/ollama.service.d"
BACKEND="${1:?usage: ollama-backend {vulkan|rocm}}"

case "$BACKEND" in
  vulkan)
    cat > "$DROPIN_DIR/backend.conf" <<'EOF'
[Service]
Environment="OLLAMA_LLM_LIBRARY=vulkan"
EOF
    ;;
  rocm)
    cat > "$DROPIN_DIR/backend.conf" <<'EOF'
[Service]
Environment="OLLAMA_VULKAN=0"
Environment="HSA_OVERRIDE_GFX_VERSION=10.3.0"
EOF
    ;;
  *)
    echo "unknown backend: $BACKEND (expected vulkan or rocm)" >&2
    exit 2
    ;;
esac

systemctl daemon-reload
systemctl restart ollama
sleep 2
systemctl is-active --quiet ollama && echo "ollama.service active, backend=$BACKEND" || {
    echo "ollama.service failed to start after switching to $BACKEND — check: journalctl -u ollama -n 50" >&2
    exit 1
}
HELPEREOF
chmod 755 "$HELPER"
log "installed $HELPER"

log "2/3: removing the standalone OLLAMA_LLM_LIBRARY=vulkan line from claude-code.conf"
# Why: that line was written by the first root-steps.sh, before this helper
# existed. The helper's own backend.conf now owns backend selection;
# leaving both would be two sources of truth for the same setting.
backup "$DROPIN_DIR/claude-code.conf"
sed -i '/OLLAMA_LLM_LIBRARY=vulkan/d; /Phase 2 Step 1: Vulkan is the preferred/,/not just an available one\./d' "$DROPIN_DIR/claude-code.conf"
log "cleaned $DROPIN_DIR/claude-code.conf"

log "3/3: switching to ROCm now, for testing"
"$HELPER" rocm

cat <<EOF

Rollback:
  sudo rm -f "$HELPER" "$DROPIN_DIR/backend.conf"
  sudo cp "$DROPIN_DIR/claude-code.conf.bak.${TS}" "$DROPIN_DIR/claude-code.conf"
  sudo systemctl daemon-reload && sudo systemctl restart ollama

To switch back and forth from now on, just:
  sudo ollama-backend vulkan
  sudo ollama-backend rocm
EOF
