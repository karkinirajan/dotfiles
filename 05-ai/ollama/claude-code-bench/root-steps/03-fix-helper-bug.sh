#!/usr/bin/env bash
# root-steps-fix-helper.sh — fixes a real bug I introduced in
# /usr/local/sbin/ollama-backend: its usage message used
# `${1:?usage: ollama-backend {vulkan|rocm}}`, and the literal, unescaped
# `{`/`}` characters inside that message confuse bash's own brace-matching
# for the `${1:?...}` expansion — the argument arrived as `rocm}` instead of
# `rocm`. Rewrites the helper without that construct, then actually
# switches to ROCm (the previous run backed up claude-code.conf and cleaned
# the OLLAMA_LLM_LIBRARY=vulkan line out of it, but crashed on this exact
# bug before ever creating backend.conf or restarting — the service is
# currently running on STALE cached environment, not the cleaned config).
#
# Run as:  sudo bash ~/ollama-setup/root-steps-fix-helper.sh

set -euo pipefail

HELPER="/usr/local/sbin/ollama-backend"

log() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

log "1/2: rewriting $HELPER without the buggy \${1:?...} usage message"
cat > "$HELPER" <<'HELPEREOF'
#!/usr/bin/env bash
# ollama-backend {vulkan|rocm} — swaps the GPU-backend drop-in and restarts
# ollama. Managed by ~/ollama-setup; part of the Claude-Code-over-Ollama
# benchmark setup. Must be run as root.
set -euo pipefail
DROPIN_DIR="/etc/systemd/system/ollama.service.d"
BACKEND="${1:-}"
if [ -z "$BACKEND" ]; then
    echo "usage: ollama-backend vulkan|rocm" >&2
    exit 2
fi

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
log "rewrote $HELPER"

log "2/2: invoking it now — switching to ROCm"
"$HELPER" rocm
