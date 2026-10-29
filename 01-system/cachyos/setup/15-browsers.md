---
title: "15 Browsers"
part: "01"
chapter: "15"
topic: browsers
versions: [firefox, brave]
last_verified: 2026-10-29
status: current
sources:
  - https://brave.com/linux/
  - https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline
  - https://mullvad.net/en/download/browser/linux
---

# 15 Browsers

## Purpose

Which browsers this machine runs, how to install each, and which extensions still work on them after Chromium dropped Manifest V2.

## 15.1 Browser strategy

| Browser | Install | Use case |
|---|---|---|
| **Brave** (default, `BROWSER=brave`) | `paru -S brave-bin` (AUR 1.98.62; the CachyOS repo copy lags by two builds) | Daily browsing and Chromium testing |
| **Firefox** | `sudo pacman -S firefox` (<!-- v:firefox -->159.0<!-- /v -->, in `packages/desktop.txt`) | Firefox testing, CSS Grid inspector, network analysis |
| **Firefox Developer Edition** (optional) | `sudo pacman -S firefox-developer-edition` (160.0b2) | Only if you want the beta channel; it is not installed on this machine |
| **LibreWolf** | `sudo pacman -S librewolf` (159.0.0, in Arch extra) | Personal browsing, banking, private accounts |
| **Mullvad Browser** | `paru -S mullvad-browser-bin` (15.0.26; Mullvad ships only apt and dnf repositories, Arch is community) | Maximum anonymity |
| **Ungoogled Chromium** | `paru -S ungoogled-chromium-bin` (156.0.8078.47; not in Arch extra) | Chrome compatibility testing |

`librewolf-bin` no longer exists in the AUR; the previous `paru -S librewolf-bin` line fails. Label: `machine-only`.

## 15.2 Manifest V2 is gone from Chromium

Chrome removed every remaining Manifest V2 extension from the Web Store on 2026-08-31, and Chromium 150 removed the MV2 code. On Brave, Ungoogled Chromium and any other Chromium browser, extensions must be MV3, with these exceptions and consequences:

- **uBlock Origin on Brave:** install the Brave-hosted MV2 build from `brave://settings/extensions/v2` (AMO's uBlock Origin is 1.75.0 as of 2026-09; the version of Brave's own hosted copy was not checked), not from the Web Store. Brave Shields already blocks ads natively, so you may not need it. Brave hosts only four MV2 extensions.
- **uBlock Origin on other Chromium browsers:** only uBlock Origin Lite is available (MV3, declarative blocking, no dynamic filtering; custom filters and external list subscriptions were added in June 2026). It is not an automatic replacement.
- **uBlock Origin on Firefox:** full MV2 build from AMO, unchanged.
- **ClearURLs:** still on Firefox (1.27.3), built on MV2; its documentation warns Chromium browsers may disable it, and Brave does not host it.

Only Firefox AMO data could be retrieved for the extensions below, so the Chromium side of each is untested. <!-- UNVERIFIED: Chrome Web Store availability and manifest version of each extension on Brave; check each listing before relying on it -->

## 15.3 Essential browser extensions

**Development:**

| Extension | Purpose |
|---|---|
| uBlock Origin (Lite on non-Brave Chromium) | Ad and tracker blocker, see 15.2 |
| React DevTools | Inspect React component tree and state |
| JSON viewer | Firefox has a built-in JSON viewer; on Chromium pick one MV3 extension (several unrelated ones share the name "JSON Viewer") |
| Wappalyzer | Identify the tech stack of a site. Closed source since August 2023, the free tier needs an account (50 lookups a month). The community rule fork `enthec/webappanalyzer` is GPLv3 |
| Refined GitHub | Enhanced GitHub UI |
| ColorZilla | Colour picker and eyedropper |

**Privacy and personal:**

| Extension | Purpose |
|---|---|
| Bitwarden | Password manager (browser extension 2026.10.0) |
| Dark Reader | Dark mode for all sites |
| Privacy Badger | EFF's adaptive tracker blocker |
| ClearURLs | Remove tracking parameters (Firefox only in practice, see 15.2) |
| SponsorBlock | Skip YouTube sponsors |

## Verify

```bash
xdg-settings get default-web-browser
pacman -Qi firefox | rg '^Version'
```

Expected: `brave-browser.desktop` and Firefox <!-- v:firefox -->159.0<!-- /v -->. Label: `machine-only`.

## Sources

- [Brave Linux install](https://brave.com/linux/), [Chrome MV2 timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline), [Mullvad Browser downloads](https://mullvad.net/en/download/browser/linux)
- Ledger: cluster C10, topics `Firefox`, `Brave`, `LibreWolf`, `uBlock Origin`, `ClearURLs` in [`LEDGER.csv`](../../../docs/modernization/LEDGER.csv)
