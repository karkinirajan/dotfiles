#!/usr/bin/env bash
set -u

target="${1:-}"
if [[ -z "$target" ]]; then
  printf 'Select a file or directory to preview.\n'
  exit 0
fi

if [[ -d "$target" ]]; then
  if command -v eza >/dev/null 2>&1; then
    eza --tree --color=always --icons --level=2 -- "$target"
  else
    ls -la -- "$target"
  fi
  exit
fi

if [[ ! -f "$target" ]]; then
  printf 'Unavailable: %s\n' "$target"
  exit 0
fi

mime="$(file --mime-type -b -- "$target" 2>/dev/null || printf 'application/octet-stream')"
case "$mime" in
  text/*|application/json|application/*xml|application/x-shellscript)
    if command -v bat >/dev/null 2>&1; then
      bat --color=always --style=numbers --line-range=:300 -- "$target"
    else
      sed -n '1,300p' -- "$target"
    fi
    ;;
  *)
    file --brief -- "$target"
    ;;
esac
