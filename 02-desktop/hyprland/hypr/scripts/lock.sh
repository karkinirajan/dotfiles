#!/usr/bin/env bash
# Run hyprlock and relaunch it if it dies without unlocking.
#
# Waking the monitor from a long DPMS-off removes and re-adds DP-2 twice; Hyprland
# disconnects clients that attach to the destroyed surfaces, which aborts hyprlock.
# With misc.allow_session_lock_restore on, a fresh locker may take over the session
# instead of Hyprland showing the permanent "lockscreen crashed" screen.
#
# Every exit is appended to $XDG_RUNTIME_DIR/hypr-lock.log.
# Usage: lock.sh   (safe to call repeatedly; only one supervisor runs at a time)
set -uo pipefail

runtime=${XDG_RUNTIME_DIR:-/tmp}
log=$runtime/hypr-lock.log

exec 9>"$runtime/hypr-lock.lock"
flock -n 9 || exit 0

# hyprlock exits 0 only after a successful unlock. While the output is being
# re-added a relaunch can fail instantly, so retry once a second for ~30s before
# giving up (a broken hyprlock config would otherwise loop forever).
#
# Hyprland exposes no session-lock state, so a non-zero exit after a long run is
# ambiguous: hyprlock may have died while locked (relaunch it) or crashed in its
# teardown right after a successful unlock (relaunching re-locks the user out).
# Cap the relaunches that follow a long run, and never reset that cap, so the
# second case re-locks a bounded number of times instead of after every unlock.
max_slow_relaunches=5
slow_relaunches=0
fast_failures=0
while :; do
    started=$SECONDS
    hyprlock
    rc=$?
    echo "$(date +%T) hyprlock exited rc=$rc after $((SECONDS - started))s" >>"$log"
    ((rc == 0)) && exit 0
    if ((SECONDS - started < 2)); then
        ((++fast_failures >= 30)) && exit 1
    else
        fast_failures=0
        if ((++slow_relaunches > max_slow_relaunches)); then
            echo "$(date +%T) giving up after $max_slow_relaunches relaunches" >>"$log"
            exit 1
        fi
    fi
    sleep 1
done
