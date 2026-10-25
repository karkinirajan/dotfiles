# Topgrade

One command (`topgrade`) that upgrades every package manager, plugin
manager, and dev toolchain on this machine in one pass. `topgrade.toml`
here is tuned to keep package-manager confirmation prompts enabled
(`assume_yes = false`), so a conflict cannot silently remove a required
package. Retry prompts are disabled, and steps are disabled only for things
that aren't actually usable on this machine:

| Step | Why disabled |
|---|---|
| `antigravity`, `antigravity_cli` | Not used on this machine |
| `helm` | Installed but has zero repos configured (`helm repo list` → empty) — nothing to update |
| `cursor` | Only `cursor-agent` CLI is installed (its own step, `cursor_agent`, stays enabled) — no actual Cursor IDE |
| `containers` | Docker daemon is intentionally disabled (`systemctl is-enabled docker` → disabled) — not started without being asked |
| `ollama` | **Only disable this temporarily** while an Ollama benchmark/inference run is in progress — an unexpected `systemctl restart ollama` mid-run corrupts results. Re-enable once the run finishes. |

## Install

```sh
sudo pacman -S --needed topgrade
```

Linked via `manifest.conf` to `~/.config/topgrade.toml` — edit either side.
