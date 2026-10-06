#!/usr/bin/env bash
# Starts a throwaway ollama server as the current user (no root), used only
# for Phase 2 backend comparison. Never touches the systemd-managed instance
# on 11434 or the real /var/lib/ollama store.
set -euo pipefail
LABEL="${1:?usage: temp-serve.sh <label> <port> [extra env already exported]}"
PORT="${2:?usage: temp-serve.sh <label> <port>}"
export OLLAMA_MODELS="$HOME/ollama-setup/test-models"
export OLLAMA_HOST="127.0.0.1:${PORT}"
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-65536}"
export OLLAMA_FLASH_ATTENTION="${OLLAMA_FLASH_ATTENTION:-1}"
export OLLAMA_KV_CACHE_TYPE="${OLLAMA_KV_CACHE_TYPE:-q8_0}"
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=10m
mkdir -p "$HOME/ollama-setup/logs"
LOG="$HOME/ollama-setup/logs/serve-${LABEL}.log"
echo "starting ${LABEL} on :${PORT} -> ${LOG}"
nohup /usr/bin/ollama serve > "$LOG" 2>&1 &
echo $! > "$HOME/ollama-setup/logs/serve-${LABEL}.pid"
