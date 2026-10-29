#!/usr/bin/env bash
# filepath: 04-editors/vscode/extensions.sh
# Install every extension ID in vscode-extensions.json. A failing install (for example a
# Microsoft-only extension on a Code - OSS build) is reported and skipped; the run does not abort.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read extensions from the JSON file
mapfile -t extensions < <(jq -r '.[]' "$SCRIPT_DIR/vscode-extensions.json")

failed=()
for extension in "${extensions[@]}"; do
  echo "Installing $extension..."
  if ! code --install-extension "$extension"; then
    echo "skip: $extension failed to install" >&2
    failed+=("$extension")
  fi
done

if ((${#failed[@]})); then
  echo "Done with ${#failed[@]} failure(s): ${failed[*]}" >&2
  exit 1
fi
echo "All extensions installed!"
