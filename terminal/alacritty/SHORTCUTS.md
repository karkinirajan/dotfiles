# Alacritty — keyboard reference

Alacritty has **no tabs and no splits** by design. Multiple terminals are
Hyprland's job (`Super+Enter`) or tmux's, which is installed. Everything below
is what the terminal itself owns; anything not listed reaches the shell, so all
zsh/fzf/starship bindings stay intact.

## Clipboard
| Key | Action |
|---|---|
| `Ctrl+Shift+C` | Copy selection |
| `Ctrl+Shift+V` | Paste from clipboard |
| `Shift+Insert` | Paste from primary selection (middle-click buffer) |
| middle-click | Paste primary selection |

Same keys as kitty. OSC 52 is set to `CopyPaste`, so a remote nvim or tmux over
SSH can also drive the local clipboard.

## Font size
| Key | Action |
|---|---|
| `Ctrl+=` or `Ctrl+Shift++` | Larger |
| `Ctrl+-` | Smaller |
| `Ctrl+0` | Reset to 11.5 |

## Windows
| Key | Action |
|---|---|
| `Ctrl+Shift+Enter` | New Alacritty window **in the current directory** |
| `Ctrl+Shift+N` | New Alacritty window (fresh, at `$HOME`) |
| `F11` | Toggle fullscreen |

`SpawnNewInstance` inherits the cwd; `CreateNewWindow` does not. That is the
only difference between the two.

## Scrollback — 20 000 lines
| Key | Action |
|---|---|
| `Ctrl+Shift+PageUp` / `PageDown` | Scroll a page |
| `Ctrl+Shift+Home` / `End` | Jump to top / bottom |
| `Shift+PageUp` / `PageDown` | Scroll a page (built-in) |
| `Ctrl+Shift+K` | Clear scrollback entirely |
| `Ctrl+Shift+L` | Clear the log notice |

`Ctrl+L` (no Shift) is the shell's own clear — it keeps scrollback.

## Search the scrollback
| Key | Action |
|---|---|
| `Ctrl+Shift+F` | Search forward |
| `Ctrl+Shift+B` | Search backward |
| `Enter` / `Shift+Enter` | Next / previous match |
| `Esc` | Leave search, stay where you are |
| `Ctrl+C` | Cancel and return to the start point |

While searching, matches are highlighted live and the viewport follows them.

## Vi mode — `Ctrl+Shift+Space`
Navigate and select with the keyboard, no mouse. Cursor turns into a block.

| Key | Action |
|---|---|
| `h` `j` `k` `l` | Move |
| `w` `b` `e` | Word forward / back / end |
| `0` `$` | Line start / end |
| `g` `G` | Buffer top / bottom |
| `Ctrl+B` `Ctrl+F` | Page up / down |
| `Ctrl+U` `Ctrl+D` | Half page up / down |
| `H` `M` `L` | Screen top / middle / bottom |
| `v` | Start selection |
| `V` | Line selection |
| `Ctrl+V` | Block selection |
| `y` | Yank selection to clipboard |
| `/` `?` | Search forward / backward |
| `n` `N` | Next / previous match |
| `Enter` | Open the URL under the cursor |
| `Esc` | Leave vi mode |

## Hints — act on text without the mouse
| Key | Action |
|---|---|
| `Ctrl+Shift+U` | Label every URL on screen; press its label to open in the browser |
| `Ctrl+Shift+O` | Label every `file:line`; press its label to open it in nvim **at that line** |
| `Ctrl` + click | Open a URL directly |

`Ctrl+Shift+O` is built for compiler and grep output — ripgrep, cargo, tsc,
eslint and pytest all print `path:line`, so you can jump straight to the error.
Labels use the home-row alphabet `jfkdls;ahgurieowpq`.

## Selection with the mouse
| Action | Result |
|---|---|
| double-click | Select word |
| triple-click | Select line |
| `Ctrl` + drag | Block (rectangular) selection |

## Config
`live_config_reload` is on — edits to `alacritty.toml` apply to running windows
immediately, no restart.

Colours are **not** in `alacritty.toml`. They come from
`themes/noctalia.toml`, which Noctalia regenerates on every palette change.
