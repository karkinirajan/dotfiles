#!/bin/bash
# Extends nightlight-toggle.sh: when night light flips on/off, also flips
# kitty's color theme and VS Code's editor theme, so the whole dev
# environment's color temperature follows one switch instead of three.
#
# ON  (hyprsunset running, warm)  -> gruvbox-dark-hard (warmer palette)
# OFF (hyprsunset stopped, cool)  -> catppuccin-mocha  (cooler palette)
#
# Called from nightlight-toggle.sh right after it flips state — reads the
# same state file rather than re-deriving it, so the two scripts can never
# disagree about current state.

STATE_FILE="/tmp/noctalia-nightlight-on"
KITTY_DIR="$HOME/.config/kitty"
VSCODE_SETTINGS="$HOME/.config/Code/User/settings.json"

if [ -f "$STATE_FILE" ]; then
  KITTY_THEME="gruvbox-dark-hard.conf"
  VSCODE_THEME="Monokai"
else
  KITTY_THEME="catppuccin-mocha.conf"
  VSCODE_THEME="Catppuccin Mocha"
fi

# --- kitty: swap current-theme.conf and live-reload every running window ---
cp "$KITTY_DIR/$KITTY_THEME" "$KITTY_DIR/current-theme.conf"
kitty @ --to unix:@mykitty set-colors -a "$KITTY_DIR/current-theme.conf" 2>/dev/null || true

# --- VS Code: patch workbench.colorTheme in-place, only if the theme
# extension is actually installed (avoid pointing at a theme that doesn't
# exist and breaking the editor's next launch) ---
if code --list-extensions 2>/dev/null | grep -qi catppuccin; then
  python3 - "$VSCODE_SETTINGS" "$VSCODE_THEME" <<'PYEOF'
import sys, re, pathlib

settings_path, theme = sys.argv[1], sys.argv[2]
p = pathlib.Path(settings_path)
text = p.read_text()

if re.search(r'"workbench\.colorTheme"\s*:', text):
    text = re.sub(r'"workbench\.colorTheme"\s*:\s*"[^"]*"',
                   f'"workbench.colorTheme": "{theme}"', text)
else:
    text = text.replace('{', '{\n  "workbench.colorTheme": "%s",' % theme, 1)

p.write_text(text)
PYEOF
fi
