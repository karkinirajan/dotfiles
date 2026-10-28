# 03.2 · Bash

Fallback `.bashrc` configuration kept for reference or interactive `bash`
subshells.

```
03-terminal/bash/
├── README.md
└── .bashrc    # reference config (not linked by manifest.conf)
```

Zsh (`/usr/bin/zsh`) is the workstation's login shell (see [`03-terminal/zsh/`](../zsh/README.md)).
`.bashrc` is kept in the repository as a standalone reference config and is not
linked by `manifest.conf` so CachyOS's default `/etc/bash.bashrc` + `~/.bashrc`
chain remains untouched unless explicitly copied.
