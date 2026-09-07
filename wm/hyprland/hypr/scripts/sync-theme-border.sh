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
import sys, re, json, pathlib, os, tempfile, tomllib


def write_atomic(path, text, validate_toml=False):
    """Replace `path` in one atomic step: write a sibling temp file, fsync it,
    then rename over the target.

    A plain `path.write_text()` truncates the file first and fills it in
    afterwards, leaving a window where anyone reading sees an empty or partial
    file. Noctalia watches settings.toml and reloads on every write — if it
    reads inside that window it finds nothing parseable, falls back to built-in
    defaults, and then SAVES those defaults, destroying the real config. That
    is not theoretical: it wiped the bar profile, every widget, the plugin list
    and the shell settings on 2026-09-07 (noctalia.log: "no config files found,
    using defaults" 1ms after this script's write). os.replace is atomic on the
    same filesystem, so a reader sees either the old file or the new one.
    """
    if validate_toml:
        tomllib.loads(text)          # never hand Noctalia something unparseable

    path = pathlib.Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        pathlib.Path(tmp).unlink(missing_ok=True)
        raise

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
write_atomic(colors_conf, conf_text)

variables_path = pathlib.Path(colors_conf_path).parent / "variables.conf"
var_text = variables_path.read_text()
end_hex = (secondary or primary).lstrip('#')
new_border = f"    col.active_border = rgba({primary.lstrip('#')}ee) rgba({end_hex}ee) 45deg"
var_text = re.sub(r'^\s*col\.active_border\s*=.*$', new_border, var_text, flags=re.M)
# Inactive: same gradient, one step dimmer (aa) rather than a different color.
new_inactive = f"    col.inactive_border = rgba({primary.lstrip('#')}aa) rgba({end_hex}aa) 45deg"
var_text = re.sub(r'^\s*col\.inactive_border\s*=.*$', new_inactive, var_text, flags=re.M)
write_atomic(variables_path, var_text)

# The topbar capsule outlines want the same accent as the bar's own border but
# dimmer, and Noctalia's color *roles* carry no alpha — so the hex has to be
# written in explicitly. Safe to write settings.toml here: theme-border-watch.sh
# only re-runs this script when the [theme] block itself changes, and this only
# touches capsule_border, so it cannot retrigger its own watcher.
settings = pathlib.Path(settings_path)
s_text = settings.read_text()
# Bar border matches the inactive window border exactly (same aa alpha);
# capsule outlines sit a step below that at 99.
new_bar = f'    border = "#{primary.lstrip("#")}aa"'
s_new = re.sub(r'^    border\s*=\s*".*"$', new_bar, s_text, count=1, flags=re.M)
new_capsule = f'    capsule_border = "#{primary.lstrip("#")}99"'
s_new = re.sub(r'^\s*capsule_border\s*=.*$', new_capsule, s_new, count=1, flags=re.M)
if s_new != s_text:
    write_atomic(settings, s_new, validate_toml=True)

print(f"synced: primary={primary} secondary={secondary}")
PYEOF

hyprctl reload
