---
title: Host package snapshot
topic: host-snapshot
last_verified: 2026-10-28
status: reference
---

# Host package snapshot

Point-in-time package records from the primary CachyOS workstation, captured 2026-10-28. They are data, not install lists: use [`../packages/`](../packages/) for what to install.

| File | Command that produced it |
|---|---|
| `pacman-explicit.txt` | `pacman -Qe` (explicitly installed, name and version) |
| `pacman-foreign.txt` | `pacman -Qm` (not in an enabled sync repository) |

Refresh both files after a deliberate package change, then re-run the package checks in [`../../../tools/`](../../../tools/README.md). Do not edit them by hand.
