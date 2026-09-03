# Zed

`zed-settings.json` → symlink or copy to `~/.config/zed/settings.json`.

## Extensions (manual install — Zed has no CLI extension installer)

The settings file wires up language servers by name that only actually work
once the matching extension is installed via Zed's own extension panel
(`Cmd/Ctrl+Shift+X` inside Zed, or the `zed: extensions` command). Install:

| Extension | Why |
|---|---|
| Python | Provides Pyright — referenced in `languages.Python.language_servers` |
| Ruff | Referenced as both formatter and language server for Python |
| TypeScript | Provides `typescript-language-server` for JS/TS/TSX/JSX |
| ESLint | `source.fixAll.eslint` code action won't fire without it |
| Tailwind CSS | Provides `tailwindcss-language-server`, wired for TSX/JSX |
| Docker Compose / Dockerfile | Language support for the `Dockerfile`/`Docker Compose` file types already declared in settings |
| TOML | `pyproject.toml`, `Cargo.toml` if relevant |
| Markdown Preview | Better markdown editing/preview than the default |

Without these, the `languages.*.language_servers` entries in
`zed-settings.json` silently no-op — Zed doesn't error, it just won't have
the LSP feature available.

## What was fixed here (2026-08-21)

The settings file had two non-functional placeholder entries left over from
copy-pasting Zed's example config — `mcp-server-github` with the literal
string `"GITHUB_PERSONAL_ACCESS_TOKEN"` as its token value (not an actual
token or env reference), and `postgres-context-server` with the example
`postgresql://myuser:mypassword@localhost:5432/mydatabase` connection
string. Both were removed rather than guessed-at, since a fake value is
worse than an absent one — re-add them with real credentials only when
actually needed for a specific project. Also removed an empty `your_agent`
custom-agent stub (`"command": "path_to_executable"`, never filled in), and
enabled `inlay_hints.enabled` (the sub-options — type/parameter/other hints
— were all already `true` but silently inactive because the master switch
was `false`, almost certainly an oversight rather than intentional).
