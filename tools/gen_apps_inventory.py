#!/usr/bin/env python3
"""Write apps-and-utils.md: every package and tool installed on this machine.

Reads the live system (pacman via expac, uv, pnpm, VS Code, Docker, hyprpm,
Noctalia) and sorts explicitly installed packages into categories by name.
Dependencies are listed by kind in an appendix. Run on the machine itself:

    python tools/gen_apps_inventory.py            # rewrite apps-and-utils.md
"""

import datetime
import json
import pathlib
import re
import subprocess
import tomllib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "apps-and-utils.md"

# Categories in reading order: (title, whole-name match, name patterns).
# The first matching category wins.
CATEGORIES = [
    ("Base system and boot", True, [
        r"base", r"base-devel", r"linux-.*", r"linux-firmware", r"amd-ucode", r"limine.*", r"mkinitcpio",
        r"efibootmgr", r"efitools", r"os-prober", r"plymouth", r"cachyos-plymouth-.*", r"sudo", r"which",
        r"less", r"man-db", r"man-pages", r"texinfo", r"lsb-release", r"logrotate", r"sysfsutils",
        r"realtime-privileges", r"dmemcg-booster", r"cachyos-hooks", r"cachyos-settings", r"cachyos-keyring",
        r"cachyos-.*mirrorlist", r"cachyos-micro-settings", r"cachyos-drm-awaiter",
        r"cachyos-kernel-manager", r"cachyos-hello", r"cachyos-packageinstaller",
        r"cachyos-benchmarker", r"chwd", r"hwdetect", r"bpftune-git", r"rebuild-detector", r"pacman-contrib",
        r"pkgfile", r"paru", r"yay", r"reflector", r"cachyos-rate-mirrors", r"accountsservice",
        r"xdg-user-dirs", r"perl", r"python", r"python-defusedxml", r"python-packaging",
    ]),
    ("Storage, filesystems and snapshots", True, [
        r"btrfs-.*", r"snapper", r"cachyos-snapper-support", r"e2fsprogs", r"xfsprogs", r"f2fs-tools",
        r"jfsutils", r"nilfs-utils", r"exfatprogs", r"dosfstools", r"mtools", r"cryptsetup", r"device-mapper",
        r"lvm2", r"mdadm", r"dmraid", r"fsarchiver", r"gparted", r"hdparm", r"smartmontools", r"sg3_utils",
        r"lsscsi", r"nfs-utils", r"kdiskmark", r"graft",
    ]),
    ("Hardware, GPU and drivers", True, [
        r"mesa-utils", r"lib32-mesa", r".*vulkan-radeon", r".*opencl-mesa", r"xf86-video-amdgpu",
        r"hip-runtime-amd", r"hipblas", r"rocblas", r"rocsolver", r"rocm.*", r"amdgpu_top", r"radeontop",
        r"nvtop", r"lact", r"cpupower", r"power-profiles-daemon", r"upower", r"openrazer-daemon", r"usbutils",
        r"usb_modeswitch", r"dmidecode", r"hwinfo", r"cpu-x", r"ethtool", r"sof-firmware", r"alsa-.*",
        r"pipewire-.*", r"wireplumber", r"pavucontrol", r"bluez.*", r"modemmanager",
    ]),
    ("Networking, VPN and security", True, [
        r"networkmanager.*", r"netctl", r"iwd", r"wpa_supplicant", r"inetutils", r"bind", r"nss-mdns",
        r"openssh", r"dnsmasq", r"dnscrypt-proxy", r"ufw.*", r"fail2ban", r"apparmor.*", r"mullvad-vpn.*",
        r"proton-vpn-gtk-app", r"xl2tpd", r"wget", r"rsync", r"syncthing", r"speedtest-cli", r"seahorse",
        r"keepassxc", r"bitwarden",
    ]),
    ("Desktop session (Hyprland and Noctalia)", True, [
        r"hypr.*", r"cachyos-hypr-noctalia", r"noctalia.*", r"sddm", r"ctwm", r"xorg-server", r"waybar",
        r"bibata-cursor-theme-bin", r"cachyos-wallpapers", r"cliphist", r"copyq", r"playerctl", r"flameshot",
        r"satty", r"swappy", r"ai-usagebar-bin", r"claudebar", r"mission-center", r"kdeconnect",
        r"ffmpegthumbs", r"ffmpegthumbnailer", r"kdegraphics-thumbnailers", r"poppler-glib", r"libgsf",
        r"libopenraw", r"libmythes", r"libdvdcss", r"gst-.*",
    ]),
    ("Fonts", True, [
        r"ttf-.*", r"otf-.*", r"noto-fonts.*", r"cantarell-fonts", r"inter-font", r"awesome-terminal-fonts",
        r"opendesktop-fonts", r"xorg-fonts-.*",
    ]),
    ("Terminals, shells and CLI utilities", True, [
        r"alacritty", r"kitty", r"tmux", r"starship", r"atuin", r"zoxide", r"direnv", r"bash-completion",
        r"cachyos-fish-config", r"cachyos-zsh-config", r"ripgrep", r"dust", r"duf", r"ncdu", r"procs", r"btop", r"glances",
        r"fastfetch", r"neofetch", r"hyfetch", r"macchina", r"yazi", r"lazygit", r"just", r"pv", r"plocate",
        r"inotify-tools", r"diffutils", r"unzip", r"unrar", r"s-nail", r"topgrade-bin", r"git", r"meld",
    ]),
    ("Editors and IDEs", True, [
        r"neovim", r"vim", r"nano.*", r"micro", r"zed", r"sublime-text-4", r"visual-studio-code-bin",
        r"pycharm-community-edition", r"antigravity-ide",
    ]),
    ("Languages, runtimes and package managers", True, [
        r"rustup", r"uv", r"nvm", r"pnpm", r"yarn", r"sccache",
    ]),
    ("Databases and data tools", True, [
        r"postgresql", r"pgvector", r"mariadb.*", r"mongodb.*", r"valkey", r"dbeaver",
    ]),
    ("Containers, cloud and DevOps", True, [
        r"docker.*", r"rootlesskit", r"slirp4netns", r"kubectl", r"k9s", r"helm", r"minikube", r"terraform",
        r"opentofu", r"pulumi", r"ansible", r"aws-cli-v2", r"azure-cli", r"gitlab-runner", r"act", r"nginx",
        r"prometheus",
    ]),
    ("AI and coding assistants", True, [
        r"ollama.*", r"claude-.*", r"claudectx-bin", r"openai-codex", r"antigravity", r"antigravity-cli",
        r"chatgtk_client-git", r"voice-agent-git", r"shelly",
    ]),
    ("Browsers", True, [
        r"firefox", r"brave-bin",
    ]),
    ("Communication and email", True, [
        r"discord", r"signal-desktop", r"slack-desktop", r"telegram-desktop", r"zapzap", r"zoom",
        r"thunderbird", r"mailspring",
    ]),
    ("Office, notes and productivity", True, [
        r"libreoffice-fresh", r"onlyoffice-bin", r"okular", r"obsidian", r"logseq-desktop-bin",
        r"anytype-bin", r"notion-app-enhanced", r"todoist-appimage", r"korganizer", r"upwork",
    ]),
    ("Media and graphics", True, [
        r"mpv", r"vlc.*", r"obs-studio", r"gimp", r"inkscape", r"spotify", r"strawberry",
        r"stremio-linux-shell", r"deluge-gtk", r"ark", r"dolphin",
    ]),
]

# Dependency kinds for the appendix, first match wins.
DEP_KINDS = [
    ("Python modules", False, [
        r"python-",
    ]),
    ("Perl modules", False, [
        r"perl-",
    ]),
    ("Haskell libraries", False, [
        r"haskell-",
    ]),
    ("Qt and KDE", False, [
        r"qt[56]-", r"kf6-", r"kf5-", r"k[a-z]+[0-9]?$", r"plasma-", r"breeze",
    ]),
    ("GTK, GLib and GNOME", False, [
        r"gtk", r"glib", r"gdk", r"gnome-", r"libadwaita", r"gsettings", r"dconf", r"at-spi", r"pango",
        r"cairo", r"harfbuzz",
    ]),
    ("ROCm and GPU compute", False, [
        r"rocm", r"hip", r"roc", r"hsa", r"comgr", r"miopen", r"rccl", r"amdsmi",
    ]),
    ("Multimedia (audio, video, GStreamer)", False, [
        r"gst", r"ffmpeg", r"libav", r"x26[45]", r"libvpx", r"dav1d", r"aom", r"svt-", r"opus", r"flac",
        r"libvorbis", r"lame", r"pipewire", r"libpulse", r"alsa", r"jack", r"libsndfile", r"libass",
        r"libdvd", r"libbluray", r"vlc-",
    ]),
    ("Fonts and font rendering", False, [
        r"ttf-", r"otf-", r"noto-", r"fontconfig", r"freetype", r"xorg-font",
    ]),
    ("X11 and Wayland", False, [
        r"xorg-", r"libx", r"xcb-", r"libxcb", r"wayland", r"libwayland", r"xkeyboard", r"libxkb", r"egl-",
        r"libdrm", r"mesa", r"vulkan-", r"spirv", r"glslang", r"lib32-",
    ]),
    ("Libraries", False, [
        r"lib", r".*-libs$", r".*lib$",
    ]),
]


def matcher(table_):
    return [(title, re.compile(("^(%s)$" if whole else "^(%s)") % "|".join(pats))) for title, whole, pats in table_]


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def clean(text):
    text = text.replace("|", "\\|").replace("\u2014", ",").replace("\u2013", "-").strip()
    return text or "(no description)"


def packages():
    out = run(["expac", "-Q", "%n\t%v\t%d"])
    rows = {}
    for line in out.splitlines():
        name, version, desc = (line.split("\t") + ["", ""])[:3]
        rows[name] = (version, desc)
    return rows


def table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines


def main():
    allpkgs = packages()
    explicit = set(run(["pacman", "-Qeq"]).split())
    foreign = set(run(["pacman", "-Qmq"]).split())

    md = [
        "---",
        "title: Installed apps and utilities",
        "topic: inventory",
        f"last_verified: {datetime.date.today().isoformat()}",
        "status: current",
        "---",
        "",
        "# Installed Apps and Utilities",
        "",
        "Everything installed on this machine, generated by `tools/gen_apps_inventory.py`",
        "from the live system (pacman, uv, pnpm, VS Code, Docker, hyprpm, Noctalia).",
        "Do not edit by hand: rerun the script after installing or removing software.",
        "",
        f"- pacman packages: {len(allpkgs)} ({len(explicit)} installed explicitly, "
        f"{len(allpkgs) - len(explicit)} as dependencies; {len(foreign)} from the AUR or built locally)",
        "- Project frameworks (Django, FastAPI, Next.js, React, Prisma and the rest) live in each",
        "  project's own environment, not system-wide; the versions the templates pin are in",
        "  [`versions.yaml`](versions.yaml).",
        "",
        "## Contents",
        "",
    ]
    sections, body = [], []

    # 1. Explicit packages by category
    placed = {}
    for pkg in sorted(explicit):
        cat = next((c for c, rx in matcher(CATEGORIES) if rx.match(pkg)), "Other applications")
        placed.setdefault(cat, []).append(pkg)
    order = [c for c, _, _ in CATEGORIES] + ["Other applications"]
    for n, cat in enumerate([c for c in order if c in placed], 1):
        sections.append(cat)
        body += ["", f"## {n}. {cat}", ""]
        rows = []
        for pkg in placed[cat]:
            version, desc = allpkgs.get(pkg, ("", ""))
            src = "AUR/local" if pkg in foreign else "repo"
            rows.append((f"`{pkg}`", version, src, clean(desc)))
        body += table(rows, ["Package", "Version", "Source", "What it is"])
    n = len(sections)

    # 2. User-level tools
    user_rows = []
    for line in run(["uv", "tool", "list"]).splitlines():
        if line and not line.startswith("-"):
            name, _, ver = line.partition(" ")
            user_rows.append((f"`{name}`", ver.lstrip("v"), "uv tool"))
    managed = pathlib.Path.home() / ".local/share/uv/python"
    if managed.is_dir():
        for d in sorted(managed.iterdir()):
            m = re.match(r"cpython-(\d+\.\d+\.\d+)-", d.name)
            if m and not d.is_symlink():
                user_rows.append(("`cpython`", m.group(1), "uv-managed Python"))
    pnpm = run(["pnpm", "ls", "-g", "--depth=0", "--json"])
    try:
        for proj in json.loads(pnpm or "[]"):
            for name, info in (proj.get("dependencies") or {}).items():
                user_rows.append((f"`{name}`", info.get("version", ""), "pnpm global"))
    except json.JSONDecodeError:
        pass
    npm = run(["npm", "ls", "-g", "--depth=0", "--json"])
    try:
        for name, info in (json.loads(npm or "{}").get("dependencies") or {}).items():
            user_rows.append((f"`{name}`", info.get("version", ""), "npm global"))
    except json.JSONDecodeError:
        pass
    if user_rows:
        n += 1
        sections.append("User-level tools (uv, pnpm, npm)")
        body += ["", f"## {n}. User-level tools (uv, pnpm, npm)", ""]
        body += table(user_rows, ["Tool", "Version", "Installed by"])

    # 3. Editor extensions
    ext = []
    try:
        for item in json.loads((pathlib.Path.home() / ".vscode/extensions/extensions.json").read_text()):
            ext.append((item["identifier"]["id"], item.get("version", "")))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    if ext:
        n += 1
        sections.append("VS Code extensions")
        body += ["", f"## {n}. VS Code extensions", ""]
        body += table([(f"`{e[0]}`", e[1]) for e in sorted(ext)], ["Extension", "Version"])

    # 4. Desktop plugins
    plug_rows = []
    for line in run(["hyprpm", "list"]).splitlines():
        m = re.search(r"Plugin (\S+)", re.sub(r"\x1b\[[0-9;]*m", "", line))
        if m:
            plug_rows.append((f"`{m.group(1)}`", "Hyprland (hyprpm)"))
    try:
        cfg = tomllib.loads((pathlib.Path.home() / ".local/state/noctalia/settings.toml").read_text())
        for pid in cfg.get("plugins", {}).get("enabled", []):
            plug_rows.append((f"`{pid}`", "Noctalia"))
    except (OSError, tomllib.TOMLDecodeError):
        pass
    if plug_rows:
        n += 1
        sections.append("Desktop plugins")
        body += ["", f"## {n}. Desktop plugins", ""]
        body += table(plug_rows, ["Plugin", "Host"])

    # 5. Containers and models
    extra = []
    for line in run(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"]).splitlines():
        if line.strip():
            extra.append((f"`{line.strip()}`", "Docker image (rootless)"))
    for line in run(["ollama", "list"]).splitlines()[1:]:
        if line.strip():
            extra.append((f"`{line.split()[0]}`", "Ollama model"))
    if extra:
        n += 1
        sections.append("Container images and local models")
        body += ["", f"## {n}. Container images and local models", ""]
        body += table(extra, ["Name", "Kind"])

    # Appendix: dependencies by kind
    deps = {}
    for pkg in sorted(set(allpkgs) - explicit):
        kind = next((k for k, rx in matcher(DEP_KINDS) if rx.match(pkg)), "Other dependencies (tools and data)")
        deps.setdefault(kind, []).append(pkg)
    sections.append("Appendix: dependencies")
    body += ["", "## Appendix: dependencies", "",
             "Pulled in by the packages above; pacman removes them with their last dependent."]
    for kind in [k for k, _, _ in DEP_KINDS] + ["Other dependencies (tools and data)"]:
        if kind not in deps:
            continue
        body += ["", f"### {kind} ({len(deps[kind])})", ""]
        body += table([(f"`{p}`", allpkgs[p][0], clean(allpkgs[p][1])) for p in deps[kind]],
                      ["Package", "Version", "What it is"])

    for i, title in enumerate(sections, 1):
        label = title if title.startswith("Appendix") else f"{i}. {title}"
        slug = re.sub(r"[^a-z0-9 -]", "", label.lower()).replace(" ", "-")
        md.append(f"- [{title}](#{slug})")
    OUT.write_text("\n".join(md + body) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}: {len(allpkgs)} packages, {len(sections)} sections")


if __name__ == "__main__":
    main()
