#!/bin/bash
# filepath: install-vscode-extensions.sh

# Read extensions from JSON file and install them
extensions=$(cat vscode/vscode-extensions.json | jq -r '.[]')

for extension in $extensions; do
  echo "Installing $extension..."
  code --install-extension "$extension"
done

echo "All extensions installed!"