---
title: Re-verification of a 20% sample
topic: verification
last_verified: 2026-10-29
status: current
---

# Re-verification of a 20% sample

Phase 4 check: 61 of the 307 `changed` ledger rows (20%, random seed 2026) were re-verified by three independent read-only subagents that fetched sources again instead of reading the ledger notes. Sites that refused access (the AUR, the Arch wiki, `github.com` advisories and some API paths) were recorded as gaps, not worked around.

| Verdict | Rows |
|---|---|
| CONFIRMED | 48 |
| PARTIAL | 12 |
| REFUTED | 0 |
| UNVERIFIABLE | 1 |

No sampled claim was refuted as a whole. The PARTIAL and UNVERIFIABLE rows and what was done about each:

| Id | Verdict | Topic | Finding | Action |
|---|---|---|---|---|
| L-0187 | PARTIAL | hyprland-config-format | Verified in v0.56.2 source: dispatchRequest branches on Config::mgr()->type() == Config::CONFIG_LUA and the legacy branch does m_dispatchers.find(first token) and returns 'Invalid dispatcher' when not found. Lua 0.55 introduction  | Repo text states only the 0.56.2 behavior, which was confirmed in source; the 0.57 message is not quoted. |
| L-0123 | PARTIAL | Wave Accounting | Pricing page confirms Starter is free (invoices estimates bills) and Pro is $19 USD/month; bank auto-import is Pro only (Starter is manual entry); extra collaborator roles are Pro (Starter has limited free access for payroll manag | Late-reminder claim dropped; country limits tagged UNVERIFIED in chapter 17. |
| L-0320 | PARTIAL | pytorch-rocm | uv PyTorch guide ROCm example uses rocm7.2 index and lists both pytorch-triton-rocm and triton-rocm as direct dependencies with sources gated on sys_platform == 'linux'; tool.uv.environments exists in uv settings. This supports th | Kept; the resolver error text is a local run in the research sandbox. |
| L-0481 | PARTIAL | Prometheus listen address | Prometheus docs: --web.listen-address exists default 0.0.0.0:9090 (so binding to 127.0.0.1:9090 is valid). Arch package file list contains /etc/conf.d/prometheus and /usr/lib/systemd/system/prometheus.service and /usr/bin/promtool | Kept; `EnvironmentFile` detail rests on older Arch package snippets. |
| L-0139 | PARTIAL | PKGBUILD design: bundled runtime vs AUR | Confirmed: Electron 36 EOL 2025-10-27; Electron 18 EOL 2022-09-27; Arch extra has electron39 (39.8.10) electron40 (40.10.6) electron44 (44.9.3) and electron36 returns 404 in extra. NOT verified: AUR upwork 5.8.0.41-5 depends on el | Kept with the Upwork README tagged UNVERIFIED for the bundled Electron version and AUR dependencies. |
| L-0194 | PARTIAL | hyprland-config-format | Wiki confirms named layer rules (name = ...), handles with set_enabled() (is_enabled() not documented further on the page), blur and xray boolean props, and namespace as a RegEx match prop. NOT verified: that 'hyprctl keyword laye | Kept; layer-rule claims in `lua-migration.md` are tagged UNVERIFIED. |
| L-0426 | PARTIAL | Docker rootless package source | Arch official search returns 0 results (not in extra); Docker rootless docs confirm dockerd-rootless-setuptool.sh creates ~/.config/systemd/user/docker.service; web search snippet names maintainer the-k. AUR RPC and package page b | Kept; AUR version and vote numbers are not stated in the repo as facts. |
| L-0545 | PARTIAL | vector-db | Versions confirmed on PyPI: chromadb 1.5.9, lancedb 0.40.0, pymilvus 3.0.2, milvus-lite 3.2.2, sqlite-vec 0.1.9, qdrant-client 1.20.0, weaviate-client 4.24.1; sqlite-vec README says pre-v1 expect breaking changes. REFUTED sub-clai | Milvus Lite index claim softened and tagged UNVERIFIED in chapter 04. |
| L-0312 | PARTIAL | zed-ollama | Page says verbatim 'deepseek-v4-flash was retired on September 25, 2026' and 'No models have been pushed' (no tags); cloud search lists deepseek-v4.1-flash (1w) and deepseek-v4-pro (2mo), no deepseek-v4-flash. So retirement and no | Retirement date corrected to 2026-09-25 in the Zed README. |
| L-0177 | PARTIAL | Stremio | README install section is 'flatpak install com.stremio.Stremio'. Releases page shows latest v1.2.2 published 07 Oct (claim says 2026-10-08; possible timezone off-by-one, year not shown). AUR stremio-linux-shell 1:1.2.2-1, maintain | Release date is not stated in the repo; Flatpak guidance kept. |
| L-0408 | PARTIAL | vite | Vite guide: 'npm 7+, extra double-dash is needed'; pnpm example is 'pnpm create vite my-vue-app --template vue' with no --; Node requirement 20.19+/22.12+; npm shows create-vite 9.3.3 and vite 8.3.5 depending on rolldown. So the r | Repo uses the documented form of the command; the silent-scaffold sub-claim is not repeated. |
| L-0083 | PARTIAL | Brave MV2 / uBlock Origin | Confirmed: Chrome timeline 'Aug 31st 2026: All remaining MV2 extensions removed from the Chrome Web Store'; uBO Lite CWS version 2026.1026.1812; AMO uBlock Origin 1.75.0 created 2026-09-16 with webRequestBlocking; Brave blog says  | Brave-hosted uBlock Origin version no longer stated; AMO version attributed to AMO. |
| L-0664 | UNVERIFIABLE | Knowledge tools | AUR returned an Anubis access-denied page for both RPC and package page; no AUR flag or version retrieved (not worked around). Web search snippets stale (show 0.10.9-2). Only adjacent data: Logseq GitHub latest release is 2.0.2 pu | Out-of-date flag could not be retrieved (AUR blocked); the repo recommends `logseq-og-bin` on other evidence. |

Smaller corrections from CONFIRMED rows: Starship: six commits touched the file, not five; corrected. Bitwarden desktop tag may be 2026-10-22; the repo says only "2026.10.1".

The row-level results are in the research scratchpad CSVs; this table is their record. A fresh re-run: pick rows from `LEDGER.csv` with `status=changed` and re-fetch each `source_url`.
