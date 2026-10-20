---
name: frontend-audit
description: Audit this project against every FRONTEND-MASTER rule. Runs the deterministic checks, has read-only auditor agents judge the rules no tool can, has a separate verifier try to refute each finding, and prints a coverage matrix. Use before a release or a client handoff, or when asked to audit or review the whole project.
disable-model-invocation: true
---

Audit the project. Do not fix anything unless the user asks afterwards.

Verdicts are tied to the current commit. If `git status --short` shows uncommitted changes, say so first and ask whether to continue; a verdict on a dirty tree is stale as soon as it is committed.

## 1. Mechanical checks

```bash
python3 audit/audit.py validate
python3 audit/audit.py run --profile ci
```

For a launch audit use `--profile launch` (this needs the app built, the local Supabase stack up, and the tools installed; see `audit/README.md`). If any rule is `FAIL`, show them and ask whether to continue with the agent pass anyway. Fixing them first is usually better.

## 2. Agent pass

```bash
python3 audit/audit.py plan
```

For each domain that has rules (`security`, `data`, `next`, `react`, `ui`, `perf`), get its rule text:

```bash
python3 audit/audit.py brief <domain>
```

Launch one `frontend-auditor` agent per domain, all in the same turn so they run in parallel. Each prompt contains the domain name, the full `brief` output, and nothing else about your conclusions. Do not tell an auditor what you expect to find.

Save each auditor's JSON reply to `audit/.work/<domain>.json` and record it:

```bash
python3 audit/audit.py record verdicts audit/.work/<domain>.json --domain <domain>
```

If `record` rejects it (missing rule, a pass without evidence, a quote that is not in the file), send the rejection text back to that same auditor with SendMessage and record the corrected reply. At most two retries per domain; after that report the domain as unaudited.

## 3. Verification

Collect every `fail` finding. Launch one `frontend-verifier` agent with them (one agent per 10 findings), then record its rulings:

```bash
python3 audit/audit.py record rulings audit/.work/rulings.json
```

## 4. Report

```bash
python3 audit/audit.py run --profile ci   # or launch, as in step 1
```

Give the user, in this order: confirmed failures (rule, `file:line`, one-line impact); rules still `AGENT` (unsure or awaiting a ruling); `NOT-RUN` checks and what each needs; `MANUAL` rules grouped by owner (`lead`, `dev`, `design`, `ops`) with the command to attest each: `python3 audit/audit.py attest <RULE> --owner <owner> --by <name> --evidence "<link or note>"`. End with the counts from `audit/report/coverage.md`.

Never present an unverified or refuted finding as a defect, and never describe an `AGENT`, `MANUAL` or `NOT-RUN` rule as passing.
