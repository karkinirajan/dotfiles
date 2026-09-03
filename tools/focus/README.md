# focus — system-wide distraction blocker

DNS + firewall blocking for CachyOS/Arch, with scheduling and a lock mode.
Blocking is enforced at the OS level (dnsmasq + nftables), so it applies to
every browser and app — not just one extension.

## How it works

```
       ┌─────────────┐
apps ─▶│ /etc/resolv │──▶ 127.0.0.1 ──▶ dnsmasq ──▶ address=/blocked/127.0.0.1
       │    .conf    │                     │
       └─────────────┘                     └──────▶ upstream 1.1.1.1 / 9.9.9.9
                                                    (for everything else)
              nftables inet filter output chain:
                  ip daddr 127.0.0.1   accept
                  ip daddr @allowed_ips accept
                  ip daddr @blocked_ips drop     ← catches DNS-caching apps
```

- **`block.list`** — domains to block. dnsmasq's `address=/domain/` covers the
  apex *and* all subdomains, so `youtube.com` also blocks `www.`/`m.youtube.com`.
- **`allow.list`** — **not** an "only these are allowed" list. It exempts those
  domains' IPs from *firewall*-level blocking, so a shared CDN address can't
  take down something you need. A domain is only ever blocked by `block.list`.

## Install

```bash
cp -r scripts ~/focus/
cp allow.list block.list schedule.conf ~/focus/
sudo cp systemd/*  /etc/systemd/system/
sudo cp networkmanager/90-focus-default-dns.conf /etc/NetworkManager/conf.d/
sudo cp dnsmasq/dnsmasq.conf /etc/dnsmasq.conf

sudo systemctl daemon-reload
sudo systemctl reload NetworkManager
sudo systemctl enable --now focus.service focus-refresh.path
sudo systemctl enable --now focus-schedule-on.timer focus-schedule-off.timer
```

The scripts hardcode `/home/kneeraazon/...`. Adjust those paths (and the
`ExecStart=` lines in `systemd/`) before using this on another machine.

## Usage

```bash
focus on                  # enable blocking system-wide
focus off                 # disable
focus status              # show current state
focus list                # show both lists
focus test <domain>       # explain why a domain is/isn't blocked
focus block <domain>...   # add to block.list  (auto-refreshes)
focus allow <domain>...   # move to allow.list (auto-refreshes)
focus lock 2h             # make the lists immutable for a period
focus schedule set 09:00 18:00
```

## Requirements

`/etc/resolv.conf` must be a **real file**, not NetworkManager's symlink into
`/run` — see the note in `networkmanager/90-focus-default-dns.conf`. Also
requires `dnsmasq`, `nftables` with an `inet filter` table containing
`allowed_ips` / `blocked_ips` sets, and `dig` (`bind-tools`).

## Known limitation: DNS-over-HTTPS

A browser with DoH enabled resolves names over HTTPS to its own provider and
never consults dnsmasq, bypassing the DNS layer entirely. The nftables
`blocked_ips` set is the backstop, but CDN IPs rotate frequently so it is
best-effort. To close this properly, disable DoH in the browser
(`network.trr.mode = 5` in Firefox) or block the DoH endpoints.

## Changelog

- **2026-09-04** — Moved the live install from `~/.focus` (hidden) to
  `~/focus`. Updated every hardcoded path: both scripts, all 8 systemd
  units, and `ollama.service`'s `PATH=` environment line (it had picked up
  `~/.focus/scripts` for the `focus` CLI's global availability). Also fixed
  a pre-existing bug in `focus status`'s "dns blocks" line: zsh prints a
  redirection-setup failure (`<file` on a missing file) straight to the
  real stderr regardless of a `2>/dev/null` on the same simple command —
  it's a shell-level failure, not the invoked command's own error, so the
  suppression never worked. Fixed by piping through `cat` instead, whose
  own (redirectable) error is what actually gets suppressed. Verified with
  a full `focus on` → `focus test` → `focus off` cycle (blocking, allowlist,
  and the `focus-refresh.path` watcher all confirmed working from the new
  location) before restoring the original off state.
