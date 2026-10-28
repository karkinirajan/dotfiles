---
title: Zed
part: "04"
chapter: "02"
topic: zed
versions: [zed]
last_verified: 2026-10-29
status: current
sources:
  - https://zed.dev/docs/
---

# Zed

`settings.json` → linked to `~/.config/zed/settings.json` by `./install.sh` via `manifest.conf`.

## Extensions

Zed 1.25 ships native support for Python (basedpyright, ruff, ty, pyright and pylsp are built in; the default Python servers are basedpyright and ruff), TypeScript/JavaScript (vtsls by default), ESLint code actions, Tailwind CSS and Markdown. Only these still need an extension, installed from the extensions panel (`Ctrl+Shift+X`) or listed under `auto_install_extensions` in `settings.json`:

| Extension | Why |
|---|---|
| Docker Compose / Dockerfile | Language support for the Dockerfile and Docker Compose file types declared in settings |
| TOML | `pyproject.toml`, `Cargo.toml` |

The older version of this page said Zed has no CLI extension installer and listed Python, Ruff, TypeScript, ESLint, Tailwind CSS and Markdown Preview as required extensions; those are native now. `settings.json` still names language servers under `languages.*.language_servers`; a name the editor does not know silently no-ops.

## Local models

`agent.default_model` is `deepseek-v4-flash:cloud` on the Ollama provider. Ollama retired that model on 2026-08-27 (its library page says so); the cloud list now shows `deepseek-v4.1-flash` and `deepseek-v4-pro`. Choosing the replacement, cloud or a local model such as `gemma4:12b`, is the owner's decision, so the setting is left unchanged. <!-- UNVERIFIED: the replacement model tag -->

`edit_predictions.provider = "ollama"` is valid in Zed 1.25 but its documented form carries an `edit_predictions.ollama` block (`api_url`, `model`, `prompt_format`); without a model it has nothing to call. The `git.git_fetch` key that used to be in `settings.json` is not a Zed setting and was removed.

## What was fixed here (2026-08-21)

The settings file had two non-functional placeholder entries left over from
copy-pasting Zed's example config, `mcp-server-github` with the literal
string `"GITHUB_PERSONAL_ACCESS_TOKEN"` as its token value (not an actual
token or env reference), and `postgres-context-server` with the example
`postgresql://myuser:mypassword@localhost:5432/mydatabase` connection
string. Both were removed rather than guessed-at, since a fake value is
worse than an absent one, re-add them with real credentials only when
actually needed for a specific project. Also removed an empty `your_agent`
custom-agent stub (`"command": "path_to_executable"`, never filled in), and
enabled `inlay_hints.enabled` (the sub-options, type/parameter/other hints

- were all already `true` but silently inactive because the master switch
was `false`, almost certainly an oversight rather than intentional).
