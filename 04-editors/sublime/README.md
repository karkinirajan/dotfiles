# 04.3 · Sublime Text

Reference configuration for Sublime Text 4 (`sublime-text-4`).

```text
04-editors/sublime/
├── README.md
├── sublime-settings.json    # Preferences.sublime-settings
├── anaconda-sublime.json    # Anaconda.sublime-settings (Python IDE plugin)
└── sublime-repl.json        # SublimeREPL.sublime-settings
```

## How to apply

These files are kept as reference material (not auto-linked by `manifest.conf`
because Sublime rewrites `Preferences.sublime-settings` in place and uses
capitalized filenames in `Packages/User/`). Copy them manually if using Sublime
Text:

```sh
mkdir -p ~/.config/sublime-text/Packages/User
cp 04-editors/sublime/sublime-settings.json \
  ~/.config/sublime-text/Packages/User/Preferences.sublime-settings
cp 04-editors/sublime/anaconda-sublime.json \
  ~/.config/sublime-text/Packages/User/Anaconda.sublime-settings
cp 04-editors/sublime/sublime-repl.json \
  ~/.config/sublime-text/Packages/User/SublimeREPL.sublime-settings
```
