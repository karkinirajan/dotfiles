#!/usr/bin/env bash
# Run install.sh against a throwaway HOME and assert it links, is idempotent and
# reports a clean status. Safe: nothing outside the temp directory is touched.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp"

cd "$repo"
./install.sh --dry-run >/dev/null
./install.sh >/dev/null
status="$(./install.sh status)"
grep -q 'everything is linked and in sync' <<<"$status" || { echo "status not clean:"; echo "$status"; exit 1; }

# Idempotent: a second run changes nothing and takes no backups.
second="$(./install.sh)"
grep -q 'backed-up 0' <<<"$second" || { echo "second run was not idempotent:"; echo "$second"; exit 1; }

# A real file in the way is backed up, not destroyed.
rm -f "$HOME/.config/starship.toml"
echo 'user content' >"$HOME/.config/starship.toml"
./install.sh >/dev/null
compgen -G "$HOME/.config/starship.toml.bak-*" >/dev/null || { echo "no backup written"; exit 1; }

echo "install.sh smoke test passed"
