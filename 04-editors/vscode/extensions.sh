#!/usr/bin/env bash
# filepath: 04-editors/vscode/extensions.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read extensions from JSON file and install them
mapfile -t extensions < <(jq -r '.[]' "$SCRIPT_DIR/vscode-extensions.json")

for extension in "${extensions[@]}"; do
  echo "Installing $extension..."
  code --install-extension "$extension"
done

echo "All extensions installed!"