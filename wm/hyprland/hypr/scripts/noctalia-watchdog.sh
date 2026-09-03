#!/bin/bash
# Runs and auto-restarts Noctalia on crash, WITHOUT wrapping it in a
# systemd --user service.
#
# Noctalia used to run as noctalia.service (added for exactly this
# auto-restart need, after observing a crash on session lock/unlock). But
# that meant every GUI app launched from Noctalia's own launcher — Chrome,
# Brave — became a child process inside noctalia.service's cgroup, and
# Chromium's sandbox cannot tolerate being nested inside a systemd service
# scope: every single app launch from the launcher crashed instantly with
# SIGSEGV (confirmed via coredumpctl — Control Group showed
# .../app.slice/noctalia.service on every crash). Apps launched any other
# way (terminal, gtk-launch) were unaffected, since they aren't children of
# that service.
#
# This loop gives the same crash-resilience — Noctalia respawns within a
# couple seconds if it dies — while keeping it a plain child process (of
# this script, which is itself a plain Hyprland exec-once child), so
# anything IT launches lands in a normal session cgroup instead.

while true; do
    /usr/bin/noctalia
    sleep 2
done
