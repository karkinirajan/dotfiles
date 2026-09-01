#!/bin/bash
# Keeps Hyprland's window border color in sync with Noctalia's active theme
# primary color, so the topbar's item borders and the window borders always
# match — even after the theme is changed later (custom palette, community
# palette, or builtin).
#
# Resolves the palette the same way Noctalia does: [theme].source picks
# custom_palette (JSON in ~/.config/noctalia/palettes/), community_palette,
# or builtin, and reads mPrimary/mSecondary from the "dark" (or "light" if
# mode=light) variant.

SETTINGS="$HOME/.local/state/noctalia/settings.toml"
COLORS_CONF="$HOME/.config/hypr/config/colors.conf"
PALETTES_DIR="$HOME/.config/noctalia/palettes"

python3 - "$SETTINGS" "$COLORS_CONF" "$PALETTES_DIR" <<'PYEOF'
import sys, re, json, pathlib

settings_path, colors_conf_path, palettes_dir = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(settings_path).read_text()

def get(key, section="theme", default=None):
    m = re.search(rf'\[{section}\]\n(.*?)(\n\[|\Z)', text, re.S)
    if not m:
        return default
    m2 = re.search(rf'^{key}\s*=\s*"([^"]*)"', m.group(1), re.M)
    return m2.group(1) if m2 else default

source = get("source", default="custom")
mode = get("mode", default="dark")

primary = secondary = None

if source == "custom":
    name = get("custom_palette")
    if name:
        p = pathlib.Path(palettes_dir) / f"{name}.json"
        if p.exists():
            data = json.loads(p.read_text())
            variant = data.get(mode) or data.get("dark") or next(iter(data.values()))
            primary = variant.get("mPrimary")
            secondary = variant.get("mSecondary")

if not primary:
    print("Could not resolve a custom palette primary color; leaving colors.conf untouched.", file=sys.stderr)
    sys.exit(1)

colors_conf = pathlib.Path(colors_conf_path)
conf_text = colors_conf.read_text()
new_mauve = f"$mauve     = rgba({primary.lstrip('#')}ff)"
conf_text = re.sub(r'^\$mauve\s*=.*$', new_mauve, conf_text, flags=re.M)
if secondary:
    new_lavender = f"$lavender  = rgba({secondary.lstrip('#')}ff)"
    conf_text = re.sub(r'^\$lavender\s*=.*$', new_lavender, conf_text, flags=re.M)
# Inactive border stays noticeably dimmer than active (~15% opacity) so the
# active window's synced accent color reads as the clear focal point.
new_dim = f"$blue_dim  = rgba({primary.lstrip('#')}26)"
conf_text = re.sub(r'^\$blue_dim\s*=.*$', new_dim, conf_text, flags=re.M)
colors_conf.write_text(conf_text)

variables_path = pathlib.Path(colors_conf_path).parent / "variables.conf"
var_text = variables_path.read_text()
end_hex = (secondary or primary).lstrip('#')
new_border = f"    col.active_border = rgba({primary.lstrip('#')}ee) rgba({end_hex}ee) 45deg"
var_text = re.sub(r'^\s*col\.active_border\s*=.*$', new_border, var_text, flags=re.M)
variables_path.write_text(var_text)

print(f"synced: primary={primary} secondary={secondary}")
PYEOF

hyprctl reload
