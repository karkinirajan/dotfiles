#!/usr/bin/env bash
# Turn the monitors on or off from hypridle and other callers.
# Usage: dpms.sh enable|disable
set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

case "${1:-}" in
    enable)  exec "$here/hypr-dispatch.sh" 'hl.dsp.dpms({ action = "enable" })'  'dpms on' ;;
    disable) exec "$here/hypr-dispatch.sh" 'hl.dsp.dpms({ action = "disable" })' 'dpms off' ;;
    *)       echo "usage: ${0##*/} enable|disable" >&2; exit 2 ;;
esac
