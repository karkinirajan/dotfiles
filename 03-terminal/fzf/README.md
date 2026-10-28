# fzf preview helper

`preview.sh` is used by the zsh fzf-tab and file-picker previews. The root
manifest links it to `~/.config/fzf/preview.sh`; it previews text with `bat`
when available, lists directories with `eza`, and falls back to standard tools.
The `file` package and other CLI dependencies are listed in
`01-system/cachyos/packages/cli.txt`.
