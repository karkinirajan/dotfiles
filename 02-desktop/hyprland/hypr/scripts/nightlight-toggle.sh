#!/bin/bash
# Reliable night light on/off, bypassing Noctalia's own gamma module.
#
# Noctalia 5.0.0_beta.10 has a confirmed, reproducible bug: once night light
# is forced on (bar icon, Control Center, or `noctalia msg
# nightlight-force-toggle`), nothing turns it back off again — force-toggle,
# nightlight-disable, and even a direct settings.toml edit + config-reload
# all silently no-op. User-confirmed live on this machine.
#
# Fix: don't use Noctalia's gamma engine at all. Use `hyprsunset`, Hyprland's
# own dedicated blue-light tool (hyprland-ctm-control-v1 protocol, separate
# from the zwlr_gamma_control path Noctalia and other clients fight over).
# State is just "is the hyprsunset process running" — nothing to get stuck.
#
# The bar icon's glyph is rewritten directly (moon-off / moon-stars) and the
# bar hot-reloaded, since Noctalia's own icon-state tracking only reflects
# its own (broken) internal nightlight state, not an external tool.

STATE_FILE="/tmp/noctalia-nightlight-on"
SETTINGS="$HOME/.local/state/noctalia/settings.toml"
TEMP_FILE="$HOME/.local/state/hyprsunset/temperature-k"

python3 - "$STATE_FILE" "$SETTINGS" "$TEMP_FILE" <<'PYEOF'
import sys, re, subprocess, os, pathlib, tempfile, tomllib

def write_atomic(path, text):
    tomllib.loads(text)
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

state_file, settings_path = sys.argv[1], sys.argv[2]
is_on = os.path.exists(state_file)

text = pathlib.Path(settings_path).read_text()
m = re.search(r'(\[widget\.nightlight\]\n)(.*?)(\n\[|\Z)', text, re.S)
if m:
    new_glyph = "moon-off" if is_on else "moon-stars"
    new_section = re.sub(r'glyph = ".*?"', f'glyph = "{new_glyph}"', m.group(2))
    new_text = text[:m.start(2)] + new_section + text[m.end(2):]
    if new_text != text:
        write_atomic(settings_path, new_text)

if is_on:
    subprocess.run(["pkill", "-x", "hyprsunset"])
    os.remove(state_file)
else:
    log = open("/tmp/hyprsunset.log", "w")
    try:
        with open(sys.argv[3]) as temperature_file:
            temperature = temperature_file.read().strip()
        if not re.fullmatch(r"[0-9]+", temperature):
            raise ValueError
    except (OSError, ValueError):
        temperature = "5500"
    subprocess.Popen(["hyprsunset", "-t", temperature], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    open(state_file, "w").close()
PYEOF

noctalia msg config-reload

# Follow the same on/off switch across terminal + editor color temperature
# (see ~/.config/hypr/scripts/nightlight-theme-sync.sh for what/why).
~/.config/hypr/scripts/nightlight-theme-sync.sh
