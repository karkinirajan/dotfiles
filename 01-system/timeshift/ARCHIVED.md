# Archived — not the active snapshot system

This module is kept for reference only. The machine actually runs
**Snapper**: `snapper`, `snap-pac`, and `cachyos-snapper-support` are
installed and `/etc/snapper/configs/root` is configured (see
`01-system/cachyos/packages/system.txt`). Timeshift itself is **not**
installed, and its own README already notes it conflicts with
`cachyos-snapper-support` — the two cannot coexist.

Don't install or enable anything in this directory without first removing the
Snapper packages; otherwise follow `README.md` in this directory as written.
