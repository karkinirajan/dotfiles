### A.21 Audit and agent kit

The templates above are the code. The audit kit is the tooling that checks a project against every rule in this file. It ships separately, installs with one command, and changes nothing in `src/`.

What it adds:

- `audit/rules.psv` maps every rule ID in this file to the named checks that prove it. `python3 audit/audit.py validate` fails when a rule has no check, a check does not exist, or a level disagrees with this file, so the map cannot drift.
- Mechanical checks: 44 structure checks, 10 SQL migration checks, 24 Semgrep rules, a live catalog query for RLS, and Playwright specs for authorization, headers, bundle budgets and the sign-in flow.
- Judgment checks: for rules no tool can decide (for example "State has exactly one owner"), read-only auditor agents return a verdict per rule with `file:line` evidence, and a separate verifier agent tries to refute each failure. A quoted line that is not in the file is rejected before it is stored.
- Human checks: rules that are decisions or dashboards (for example SB-08 auth settings) need a dated attestation by an owner.
- Claude Code agents (`frontend-engineer-kit` preloads `frontend-master`; `frontend-engineer` is the generic one; `frontend-auditor` and `frontend-verifier` are read-only), the `frontend-master` skill (originally generated from this file; the references are now edited in place), and the `/frontend-audit` skill that runs the whole pass.

Statuses: `PASS` means every mapped check ran and passed. `FAIL`, `NOT-RUN` (a tool or service was missing), `AGENT` (needs a verdict for this commit), `MANUAL` (needs an attestation), `WAIVED` (unexpired entry in `audit/waivers.json`, GOV-04), `N/A`, `INFO` (MAY rules). "Meets 100 percent" means no rule is anything other than `PASS`, `N/A`, `INFO` or `WAIVED`, which the launch profile enforces.

```bash
python3 audit/audit.py validate
python3 audit/audit.py run --profile ci       # static, SQL, Semgrep; runs in CI
python3 audit/audit.py run --profile launch   # also tools, e2e, live RLS; needs the stack and a build
```

Verdicts are tied to a commit and ignored when `HEAD` moves. `audit/verdicts.json`, `audit/.work/` and `audit/report/` are git-ignored output. Attestations (`audit/manual.json`) and waivers are committed.
