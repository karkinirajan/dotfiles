---
title: Host package snapshot
topic: host-snapshot
last_verified: 2026-11-16
status: reference
---

# Host package snapshot

Point-in-time package records from the primary CachyOS workstation, captured 2026-11-16: 280 explicitly installed packages, 27 foreign, 1,383 installed in total. The previous capture (2026-10-28) had 324 and 30; the difference is the trim of 2026-11-12 (see [`../workstation-changes.md`](../workstation-changes.md)). They are data, not install lists: use [`../packages/`](../packages/) for what to install.

| File | Command that produced it |
|---|---|
| `pacman-explicit.txt` | `pacman -Qe` (explicitly installed, name and version) |
| `pacman-foreign.txt` | `pacman -Qm` (not in an enabled sync repository) |

Refresh both files after a deliberate package change, then re-run the package checks in [`../../../tools/`](../../../tools/README.md). Do not edit them by hand.
