---
title: Building a production-grade Claude Code agent
part: "05"
chapter: agent-dev
topic: agent-dev
last_verified: 2026-11-13
status: current
---

# Building a production-grade Claude Code agent

An ordered, repeatable procedure for taking an agent from an idea to something you can launch, share and maintain. Follow the steps in order. Every step has a goal, the actions, a deliverable and a gate. Do not start a step until the gate of the previous one is met.

The guide is built from three things: the current official documentation, Anthropic's published engineering guidance on agents, and what was learned building a real agent in this repository (`repo-modernizer`, distilled from 67 repository modernizations and tried on a throwaway fixture).

## How to read this guide

- A tag such as `[S4]` points to a source in Appendix F. The tag `[L]` means the statement was checked against the installed Claude Code (2.1.322) on 2026-11-13.
- "Not stated" means the sources do not say. Do not fill the gap from memory: test it.
- "Recommendation" marks advice that is judgment, not documentation.
- The documentation changes quickly. Before a launch, re-check the facts in Steps 5, 9, 10 and 13 against the live pages.

## The bar: what "production-grade" means here

Ten criteria. The launch checklist in Step 14 is these ten, made testable.

| # | Criterion | Proven by | Step |
| --- | --- | --- | --- |
| 1 | One clear job, with written non-goals | The spec | 2 |
| 2 | Routes reliably: it is chosen for the right requests and not for the wrong ones | Trigger tests | 8, 10 |
| 3 | Least privilege: a minimal tool allowlist, and deterministic guards for every must-never rule | Settings, hooks, the tool list | 3, 7 |
| 4 | A prompt at the right altitude: structured, with defaults for decisions and a fixed output contract | Review against Step 5 | 5 |
| 5 | Heavy knowledge lives in progressive-disclosure files, not in the always-loaded prompt | Line counts, `plugin details` | 6 |
| 6 | Measured against a baseline without the agent, and exercised on a realistic fixture | Eval results, fixture transcript | 8, 10 |
| 7 | Bounded: turn limit, budget, stop conditions, resumable state | Config and a forced-stop test | 3, 11 |
| 8 | Observable: transcripts, a structured final report, debuggable failures | A transcript you can read | 11, 15 |
| 9 | Honest documentation: what it does, what it needs, what was not verified | The README | 12 |
| 10 | Versioned, validated in CI, and installable by someone else | `validate --strict`, install test | 13 |

## Roadmap

| Step | Name | Deliverable | Gate |
| --- | --- | --- | --- |
| 1 | Decide it should be an agent | A one-line decision with the alternatives rejected | Simpler options ruled out |
| 2 | Write the spec | `SPEC.md`, one page | The five run questions answered |
| 3 | Design the architecture | A layer map, tool list, limits | Every must-never rule has an enforcement mechanism |
| 4 | Scaffold | The repository layout | Layout validates |
| 5 | Write the agent file | `agents/<name>.md` | Review checklist passes |
| 6 | Write the playbook | `skills/<name>/` | SKILL.md under 500 lines, references one level deep |
| 7 | Enforce rules deterministically | Deny rules, hooks | A blocked action is actually blocked |
| 8 | Build the evals first | `evals/`, baseline results | At least 20 realistic cases, baseline recorded |
| 9 | Validate statically | A clean `validate --strict` | Exit 0 |
| 10 | Test dynamically | Fixture run, eval run, transcript review | Thresholds met, zero rule violations |
| 11 | Harden | Stop conditions, resumability, caps | Forced-stop test passes |
| 12 | Document | `README.md`, `CHANGELOG.md` | A stranger can install and run it |
| 13 | Package and distribute | `plugin.json`, `marketplace.json`, a tag | Install works from a clean machine |
| 14 | Launch checklist | A signed-off checklist | All items checked |
| 15 | Operate and improve | Regression evals, a change log | Each incident becomes an eval case |

---

## Step 1. Decide it should be an agent

**Goal.** Choose the simplest mechanism that does the job. Anthropic's guidance is to find "the simplest solution possible" and add complexity only when it demonstrably improves outcomes [S11].

**Do.**

1. Write the job in one sentence. If it contains "and" between two unrelated jobs, you have two agents.
2. Match the need to a mechanism:

   | Need | Use | Source |
   | --- | --- | --- |
   | Facts that must always be known | `CLAUDE.md`, kept short | [S4] |
   | A procedure loaded only when relevant | A skill | [S3] [S5] |
   | Something that must happen every time, with no exceptions | A hook or a deny rule | [S4] |
   | A workflow you start yourself, with side effects | A skill with `disable-model-invocation: true` | [S4] |
   | Work that needs isolated context, a narrow tool set, parallel runs or an independent reviewer | A subagent | [S4] |
   | A fixed sequence with a predictable path | A script or a workflow, not an agent | [S11] |
   | An agent inside your own product | The Agent SDK `agents` option | [S9] |

3. Ask the three questions. Is the path predictable? Does the work need model-directed exploration? Would one prompt plus a skill be enough? Recommendation: build an agent only when the path is not predictable and one prompt is not enough.
4. Note the cost. A subagent pays off for parallel work, noisy output, independent review and narrower tools, but its cost is mostly tokens and a fresh subagent can end up slower [S4]. Agents use about 4 times the tokens of a chat, and multi-agent systems about 15 times [S13].

**Deliverable.** A one-line decision: "An agent, because ...; not a skill, because ...".

**Gate.** The simpler options are named and ruled out in writing.

---

## Step 2. Write the spec

**Goal.** Fix what "done" means before writing a single prompt line. This is the same set of questions the best-practices guide asks before you leave a run unattended: done condition, self-checking, scope, limits, and sign-off [S4].

**Do.** Write `SPEC.md` with these headings:

| Heading | Content |
| --- | --- |
| Job | One sentence |
| Triggers | Five example requests that should select the agent |
| Non-triggers | Five similar requests that should not |
| Inputs | What the caller must give (for example an absolute path) |
| Outputs | Artifacts it creates and the exact shape of the final report |
| Done condition | Observable, checkable facts |
| Self-check | The commands the agent runs to prove its own work |
| Scope | What it may touch and what it must not |
| Limits | Turns, spend, time |
| Sign-off | What a human must approve, and what the agent hands over instead of doing |
| Autonomy | Can it ask questions? Subagents cannot: the sources list `AskUserQuestion` among the tools removed from subagents [S1] |
| Risk tier | Reads only, writes locally, uses the network, has external effects |
| Hard rules | The must-never list, one line each |
| Non-goals | What it is deliberately not for |

**Deliverable.** `SPEC.md`.

**Gate.** A colleague can read the spec and predict what the agent will do with a given input.

---

## Step 3. Design the architecture

**Goal.** Decide where every piece of knowledge and every control lives, before you write them.

**Do.**

1. Map the layers:

   | Content | Goes in | Why |
   | --- | --- | --- |
   | Identity, hard rules, start and stop conditions, output contract | The agent body (system prompt) | Always present |
   | The procedure and its checklists | A skill, preloaded with `skills:` when it is needed on every run | Loaded at startup: the full content is injected, up to 32 names [S1] |
   | Large references, catalogues, templates | Files under the skill (`references/`, `templates/`), read on demand | Only their use costs tokens [S5] |
   | Deterministic operations | Scripts that are executed, not read | Only the output consumes tokens; more reliable than generated code [S5] |
   | Must-never rules | `permissions.deny`, hooks | Enforced; prompts are not [S4] |
   | Lessons learned across runs | `memory:` | Persists between conversations [S1] |

2. Set the context budget. The aim is "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome" [S14]. Start with a minimal prompt on the strongest model you will use, then add instructions and examples only for failures you observe [S14]. After the scaffold exists, `claude plugin details <name>` prints a plugin's component inventory and projected token cost [L].
3. Choose the tools. Give an allowlist, not "all tools":
   - `tools:` takes a comma-separated string or a YAML list, and omitting it inherits every tool available to subagents, MCP tools included [S1].
   - MCP tools use `mcp__server__tool`, and `mcp__server__*` allows a whole server [S1].
   - Whatever you list, the harness removes `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless the mode is plan), `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`, and `Agent` at the depth limit [S1]. Design for that.
   - Background subagents keep every MCP tool but only a fixed list of built-in tools (including `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`, `Skill`) [S1].
   - If you build your own tools: build few, consolidate multi-step operations into one tool, namespace by service and resource, use unambiguous parameter names, return high-signal fields, offer a concise response mode, truncate with sensible defaults, and write errors that say how to fix the call [S12].
4. Choose model and effort. Use `model: inherit` unless you have a measured reason. Haiku "is a good fit for subagents doing simple jobs" [S4]. Effort accepts `low`, `medium`, `high`, `xhigh`, `max`, depending on the model [S1]. Test with every model you intend to support: Haiku needs enough guidance, Opus tolerates less explanation [S5].
5. Set the limits:
   - `maxTurns` stops the subagent at the limit and marks the output partial, and Claude can resume it [S1]. No default and no upper bound are stated [S1].
   - `--max-budget-usd` stops a headless run at an estimated spend (print mode only; subagent spend counts; spend can exceed the cap) [S8] [L].
   - `--max-turns` is documented for print mode with no default limit [S8], but `claude --help` on 2.1.322 does not list it [L]. Test it before you rely on it.
6. Set permissions. A subagent inherits the parent's permission rules, and deny rules apply to subagents [S1]. If the main conversation is in `bypassPermissions`, `acceptEdits` or auto mode, the subagent runs in that mode and `permissionMode` is ignored [S1]. Deny rules hold in every mode, including auto and `bypassPermissions` [S4]. For locked-down CI, `dontAsk` denies every call that would prompt [S8].
7. Decide single or multi-agent. Start with one agent. Multi-agent fits breadth-first work with independent directions, and does not fit work that needs shared context or has many dependencies, which includes most coding tasks [S13]. If you do orchestrate, each delegated task needs an objective, an output format, guidance on tools and sources, and clear task boundaries, and the prompt should state how effort scales with task size [S13].
8. Decide on memory (`user`, `project`, `local`), `isolation: worktree` (a temporary git worktree branched from the default branch) and `background` [S1]. Recommendation: use `isolation` only when the agent must not touch the working tree, and note that it does not suit work that depends on the current branch or on untracked files.

**Deliverable.** `ARCHITECTURE.md`: the layer map, the tool list with a reason per tool, the limits, the permission stance.

**Gate.** Every must-never rule in the spec has an enforcement mechanism in the architecture (Step 7), not just a sentence in a prompt.

---

## Step 4. Scaffold

**Goal.** Start in a git repository with the layout that packaging will need later.

**Do.**

1. Create the repository and use this layout. Only `plugin.json` goes inside `.claude-plugin/`; everything else sits at the plugin root [S2].

   ```text
   my-agent/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── agents/
   │   └── my-agent.md
   ├── skills/
   │   └── my-playbook/
   │       ├── SKILL.md
   │       ├── references/
   │       └── templates/
   ├── hooks/
   │   └── hooks.json            optional
   ├── evals/                    created in Step 8
   ├── README.md
   ├── LICENSE
   ├── CHANGELOG.md
   └── SPEC.md
   ```

2. Or let the CLI scaffold it: `claude plugin init <name> --with agents skills` writes the plugin to `~/.claude/skills/<name>/` and it loads next session as `<name>@skills-dir` [L]. Give the components as a space-separated list; a comma-separated value such as `agents,skills` is rejected [L]. Choose from `skills`, `agents`, `hooks`, `mcp`, `lsp`, `output-style`, `channel` [L].
3. Personal setups that keep `~/.claude` in version control (as this repository does) can place the files directly in `agents/` and `skills/` and package later.
4. Test the layout in a session without installing: `claude --plugin-dir ./my-agent`. After edits, run `/reload-plugins` [S2].

**Deliverable.** A committed skeleton.

**Gate.** `claude plugin validate ./my-agent` exits 0 [L].

---

## Step 5. Write the agent file

**Goal.** A system prompt that a model can follow exactly, and a description that routes correctly.

**Do.**

1. Write the frontmatter. Only `name` and `description` are required, and unrecognized fields are ignored silently, so a typo fails without a message [S1]. Appendix A lists every field.
2. Write the description. It is what Claude reads to decide whether to delegate, so it must pick this agent and not another [S1].
   - Say what it does, when to use it, and the requests that trigger it. Name the inputs it needs. Add a "Not for" clause.
   - Keep it brief. Combined descriptions over 15,000 tokens trigger a startup warning [S1].
   - To encourage proactive delegation, include a phrase such as "use proactively" [S1].
   - For skills, write in the third person and say both what it does and when to use it; avoid vague text such as "Helps with documents" [S5]. Recommendation: apply the same rules to agents.
3. Write the body in this order. Appendix B is a fill-in template.
   1. Role: two sentences.
   2. Start: validate the inputs, detect a resume, read the first files.
   3. Hard rules: a numbered list, each rule testable by looking at a transcript.
   4. Procedure: the phases, referring to the skill for detail.
   5. Decisions without asking: a defaults table, because a subagent cannot ask [S1].
   6. Stop conditions: the exact cases for BLOCKED and PARTIAL.
   7. Output contract: a fixed report format.
4. Apply the style rules:
   - Aim at the "right altitude": between brittle if-else logic and vague guidance that assumes shared context. Organize into labeled sections. "Minimal does not necessarily mean short" [S14].
   - State what to do rather than narrating how or why [S3].
   - Do not rely on emphasis. The best-practices guide lists "IMPORTANT" and ALL CAPS among old habits to stop, and says a rule you keep emphasizing belongs in a hook [S4].
   - Prefer a few diverse canonical examples to a long list of edge cases [S14].
   - Use one term for one thing throughout [S5].
   - Keep time-sensitive facts (versions, dates) out of the prompt. Put them where they can be re-checked [S5].
   - Do not duplicate the skill in the agent body. The body holds rules and contracts, the skill holds the procedure.
5. If the agent spawns agents, teach it how to delegate: objective, output format, tools and sources, boundaries, and effort scaling [S13].

**Deliverable.** `agents/<name>.md`.

**Gate.** Review checklist:

- [ ] The description names the triggers, the inputs and a "Not for".
- [ ] `tools:` is an allowlist with a reason for each entry (in `ARCHITECTURE.md`).
- [ ] Every hard rule is testable and has an enforcement mechanism where one exists.
- [ ] Defaults exist for every decision a subagent cannot ask about.
- [ ] The output contract is a fixed shape.
- [ ] No time-sensitive fact is hard-coded.

---

## Step 6. Write the playbook (the skill)

**Goal.** Move the long procedure out of the prompt and make it load only as needed.

**Do.**

1. Create `skills/<name>/SKILL.md`. Rules from the documentation:
   - Keep the body under 500 lines and split into files before you reach it [S3] [S5].
   - Name: lowercase letters, numbers and hyphens, at most 64 characters, and not containing `anthropic` or `claude` [S5]. Those are the Agent Skills platform's limits; the Claude Code page states no length or charset rule for names [S3], but following the stricter rule keeps a skill portable. Description: non-empty, at most 1,024 characters [S5]. The description plus `when_to_use` is truncated at 1,536 characters in the skill listing [S3].
   - Startup loads only name and description. The body loads when the skill becomes relevant, and further files only as needed [S5].
   - Keep references one level deep from `SKILL.md`; deeper nesting leads to partial reads. Give files over 100 lines a table of contents [S5].
2. Choose the degree of freedom per instruction. Use low freedom (exact commands, "do not add flags") for fragile operations, medium for a preferred pattern, high where many approaches are valid [S5].
3. Put deterministic work in scripts. Say whether Claude should run a script or read it. Solve errors inside the script, and justify every constant [S5].
4. Add feedback loops: run a validator, fix, repeat, and say "only proceed when validation passes" [S5]. Give complex workflows a copy-paste checklist [S5].
5. Preload with `skills:` in the agent only when every run needs the playbook. The full content is injected for each listed skill, so keep it compact; skills with `disable-model-invocation: true` cannot be preloaded [S1].
6. Mind the security of the skill itself. `allowed-tools` in a skill grants permission for the invoking turn only and does not restrict other tools; review it in any skill you did not write [S3].

**Deliverable.** A skill directory with `SKILL.md`, `references/` and `templates/`.

**Gate.** `wc -l skills/*/SKILL.md` is under 500; every reference is linked from `SKILL.md`; no reference links to another reference.

---

## Step 7. Enforce the rules deterministically

**Goal.** Make the must-never rules impossible to break, instead of unlikely to be broken.

**Do.**

1. Sort every rule from the spec:

   | Rule type | Mechanism | Notes |
   | --- | --- | --- |
   | Never run a command | `permissions.deny` in settings | Deny rules are checked before allow rules and apply to subagents [S1] [S4] |
   | Never touch a path | A `PreToolUse` hook, exit code 2 | Exit 2 blocks; exit 1 does not [S7] |
   | Must verify before finishing | A `Stop` hook (or `SubagentStop`), exit 2 | Stop hooks end the turn after eight blocks with no tool call between them, adjustable with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` [S4] [S7] |
   | Never add attribution text to commits | The `attribution` setting (`"attribution": false`), plus a `PreToolUse` hook that refuses a commit command containing a trailer | The setting needs Claude Code 2.1.281 or later; whether it governs subagents is not stated, and matching commit-message text in a hook is not a documented feature, so test both [S15] |
   | Limit the tool surface | `tools` / `disallowedTools` | Enforced by Claude Code [S4] |
   | Confine Bash and the network | The sandbox | A `Read` deny catches `cat .env` but not a script that opens the file; a `WebFetch` deny does not stop `curl` unless the sandbox is on [S4] |
   | Style and judgment | The prompt | Not enforceable. Do not pretend otherwise |

2. Know the limits of hooks:
   - Exit 2 is the blocking code. Any other non-zero code is non-blocking and the action proceeds [S7].
   - `onFailure: "block"` makes a crashed or timed-out hook block [S7] [S4].
   - A `PreToolUse` hook receives the tool call on stdin; for Bash the command string is `tool_input.command`. A handler can narrow itself with `if`, written in permission-rule syntax such as `Bash(git commit *)`. Exit 2 stops the call before permission rules are evaluated [S15].
   - A Bash deny rule matches the command text as written. `Bash(git push *)` does not stop `git -C . push origin main`, and `Bash(curl *)` does not stop `/usr/bin/curl` or `sh -c 'curl ...'`. The permissions page says a Bash rule is not a security boundary around the program and points to the sandbox or a `PreToolUse` hook [S15]. List the bypass forms as separate rules, and test each one.
   - `prompt` and `agent` hooks ask another model, so they are not deterministic. Use `command` or `http` for enforcement [S4].
   - Hooks defined in a plugin agent's frontmatter are ignored, as are `mcpServers`, `permissionMode` and `initialPrompt`. Put them in the plugin's `hooks/hooks.json` or MCP config instead [S2].
   - Hooks in a project subagent's frontmatter run only after the workspace trust dialog is accepted [S7].
3. Keep it small. Hooks that enforce only preferences should be deleted [S4].

**Deliverable.** Deny rules and hooks, each with a test (a command that must be refused).

**Gate.** For every must-never rule, a deliberate attempt in a scratch session is blocked.

---

## Step 8. Build the evals first

**Goal.** Know how you will measure the agent before you tune it. The skills guide says to create evaluations before writing extensive documentation [S5].

**Do.**

1. Collect about 20 realistic cases from real use. Large effects are visible with few cases, and waiting for hundreds delays learning [S13].
2. Cover four kinds of case:

   | Kind | Example | Grader |
   | --- | --- | --- |
   | Trigger, positive | A request that should select this agent | `tool_used` (the sources document it for the `Skill` tool; for the `Agent` tool, confirm it works before relying on it) |
   | Trigger, negative | A neighbouring request that should not | The absence of that tool call |
   | Outcome | A fixture task with a checkable end state | `file_exists`, `regex`, an `llm` rubric |
   | Rule adherence | Bait: a request to add a forbidden trailer, a file that must not be read | `tool_order`, `regex` on the transcript, `file_exists` with `exists: false` |

3. Prefer outcome checks to process checks. For agents that change state, judge whether the final state is right, not the exact path, because correct runs differ [S13].
4. Use a rubric for the qualitative checks: factual accuracy, completeness, tool efficiency, a 0.0 to 1.0 score and a pass or fail [S13]. Add human review, since "manual testing remains essential" [S13].
5. Write the cases for `claude plugin eval` (Appendix C):
   - Suite location: `evals/` under the plugin root, or the manifest's `experimental.evals` value [S6] [L].
   - Each case is a directory with `prompt.md` and/or `case.yaml`, and `graders/<name>.md`. A case with no grader fails to load [S6].
   - `claude plugin eval init --bare <name>` writes a blank case; without `--bare` it runs an authoring interview in a terminal [L].
6. Capture the baseline: by default the tool runs each case with the plugin and without it and reports the difference [L]. Graders marked with-only, including `tool_used: Skill`, indicate that the plugin fired and are not part of the score [L].
7. Test with every model you plan to support [S5].

**Deliverable.** `evals/` with at least 20 cases and a recorded baseline.

**Gate.** The baseline run completes and the without-agent score is recorded, so you can show what the agent adds.

---

## Step 9. Validate statically

**Goal.** Catch every error that needs no model.

**Do.**

1. Run the validator. `claude plugin validate <path> [--strict] [--json] [--profile directory]` [L]:
   - Exit 0 passed (with or without warnings), exit 1 failed, exit 2 an unexpected error [S2].
   - `--strict` turns warnings, such as unrecognized fields and missing metadata, into failures. Use it in CI [L].
   - `--profile directory` also fails on what the plugin directory would refuse, such as a missing README, and says the directory also runs a safety scan and a policy review that the command does not [L].
   - It validates a directory of agents, skills and commands as well as a manifest [L].
2. Check by hand what the validator cannot:
   - Frontmatter field names against Appendix A (unknown names are ignored silently).
   - `SKILL.md` length, description length, reference depth, links.
   - No secret or personal data in any file (`git grep` your own patterns; use count-only scans).
   - The prompt contains no stale model names or dates.
3. Lint the Markdown and the scripts with the same tools you use elsewhere.

**Deliverable.** A clean validation report saved with the build.

**Gate.** `claude plugin validate . --strict` exits 0.

---

## Step 10. Test dynamically

**Goal.** Prove it works on realistic work and that the rules hold.

**Do.**

1. **Fixture run.** Build a small throwaway project with planted problems, and bait for each hard rule: a secret in history, an uncommitted file the agent must not touch, a file it must not read. Run the agent on it with only the task and its input, no hints. Appendix E shows this test applied to `repo-modernizer`.
2. **Read the transcript.** Subagent transcripts are written to `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl` [S8]. Look for wasted calls, the wrong tool, a rule that was bent, a question it should not have needed. Many redundant calls suggest limits or descriptions that need work [S12].
3. **Trigger tests.** In fresh sessions, send each trigger and non-trigger prompt and record whether the agent or skill fired. Seeing a skill trigger "tells you Claude found it, not that it did what you intended" [S3].
4. **Eval run.** For example, from the documented CI invocation [S6]:

   ```bash
   claude plugin eval . --trust-plugin --json results.json --threshold 0.8 \
     --judge-model haiku --no-publish --max-cost-usd 20
   ```

   - Each run is a `claude -p` child with only the plugin loaded, in a temporary home and working directory; your settings, hooks, CLAUDE.md, MCP servers and other plugins are absent [S6].
   - Read-only tools are granted by default. Grant more with `--allow-tools`, for example `Bash`, which runs under the OS sandbox and is refused if none is available [S6] [L].
   - Exit codes: 0 passed; 1 a case below the threshold, a load error, no cases, an untrusted directory without `--trust-plugin`, an API error or an invalid option; 2 a partial run (cost ceiling hit or a credential rejected); 130 interrupted; 143 terminated [S6].
   - Results are written to `results/<timestamp>/` as `aggregate-result.json` and `report.html` [S6].
5. **Headless run.** Run the agent the way automation would: `claude -p --agent <name> --output-format json --max-budget-usd <n>` [L]. Output formats are `text`, `json` and `stream-json`; `json` includes `result`, `session_id` and `total_cost_usd` [S8]. A `-p` run with no permission mode set starts in manual mode and denies calls that need approval [S8]. Pre-approve specific commands with `--allowedTools`, and use `--permission-prompts none` for unattended runs [S8] [L]. Trial on a few inputs first [S4].
6. **Iterate on the failure the transcript shows.** Change one thing, rerun the affected cases, then the whole suite for regressions. Hold out some cases to avoid overfitting [S12].

**Deliverable.** The eval report, the fixture transcript, and a list of fixes made.

**Gate.**

- [ ] The score is at or above the threshold you set and clearly above the baseline.
- [ ] Zero rule violations across all fixture and bait runs.
- [ ] Trigger tests: every positive fires and no negative fires.
- [ ] The headless run finishes inside its caps.

---

## Step 11. Harden

**Goal.** Make failure safe, visible and recoverable.

**Do.**

1. **Resumability.** Agents are stateful and errors compound, so design for resuming from where it stopped, not restarting [S13]. Write progress to a file outside the conversation after every phase; structured note-taking is the documented technique for long work [S14]. Tell the agent to read that file first on start.
2. **Turn budget.** At the limit the output is partial and the subagent can be resumed [S1]. Add a rule: past about two thirds of the budget without reaching the final checks, stop adding scope and report partial (Recommendation).
3. **Stop conditions.** List exactly when the agent reports BLOCKED, and make it say what a human must do.
4. **Untrusted input.** Treat everything fetched or read from outside as data. Relay instruction-shaped text as a finding, never follow it.
5. **Secrets and privacy.** Count-only scans, no secret values in output or logs, no personal data in requests to outside services.
6. **Cost control.** Caps on spend and turns; know that subagent spend counts toward the total [S9]. The defaults are three levels of nesting and 20 concurrent subagents, changed with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` [S1] [S9].
7. **Idempotence.** Re-running on the same input must not duplicate work or damage earlier results.
8. **Tool failures.** For each tool the agent relies on, define what to do when it is missing or down (for example, mark a check "written, not run").
9. **Failure modes seen in published multi-agent work**, to guard against explicitly: spawning far too many subagents for a simple query, searching endlessly for sources that do not exist, continuing after enough results, and over-investing in simple queries [S13].

**Deliverable.** A hardening section in `ARCHITECTURE.md` and a passing forced-stop test: interrupt a run mid-way, restart it, and confirm that it resumes without repeating or damaging work.

**Gate.** The forced-stop test passes.

---

## Step 12. Document

**Goal.** Let a stranger install it, use it correctly and know its limits.

**Do.**

1. Write `README.md` (at least 40 words is the directory's floor [L]; write far more). Include: what it does and when not to use it; install commands; how to invoke it with two real examples; inputs and outputs; the permissions and tools it needs; what it will never do; limits and cost expectations; a "Not verified" list; troubleshooting.
2. Keep a `CHANGELOG.md`. Every behavior change in the prompt is a release.
3. Add a LICENSE file or set `license` (an SPDX id) in `plugin.json` [L].
4. Add an icon if you will submit to the directory: a square PNG or JPEG, 512 to 2048 px on each side, under 2 MB; SVG and WebP are not accepted [L].
5. Add `documentationUrl`, `supportUrl` and `privacyPolicyUrl` to `plugin.json` if the agent touches user data [S2].

**Deliverable.** README, CHANGELOG, LICENSE.

**Gate.** Someone who has not seen the project installs it from the README alone and runs the first example.

---

## Step 13. Package and distribute

**Goal.** Make it installable, versioned and reviewable by others.

**Do.**

1. **Manifest.** `.claude-plugin/plugin.json` requires only `name` (kebab-case; names beginning `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` are errors). Add `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `version` [S2].
2. **Component paths** are relative to the plugin root, start with `./`, and may not escape it. `agents` entries must be `.md` files, not directories [S2].
3. **Namespacing.** Plugin agents are invoked as `<plugin>:<name>` (for example `my-plugin:security-reviewer`); skills as `/<plugin>:<name>` [S2].
4. **Versioning.** `version` is a string "not checked against semver", and setting it pins the plugin until you change it. If it is set and you push without changing it, users keep the old copy. If unset, the commit SHA is the version [S2]. Recommendation: set it, bump it on every release, and keep the changelog in step.
5. **Tag releases:** `claude plugin tag --dry-run`, then `claude plugin tag --push`. It creates `<name>--v<version>` and checks that `plugin.json` and any marketplace entry agree [L].
6. **Host a marketplace.** Add `.claude-plugin/marketplace.json` with `name`, `owner` and `plugins[]`, each plugin entry having `name` and `source`. A plugin in the same repository uses `"source": "./"`. There is no submission form for your own marketplace; whoever can clone the repository can install, so a private repository gives a private marketplace [S2].
7. **Install, the way a user will:**

   ```bash
   claude plugin marketplace add <owner>/<repo>
   claude plugin install <plugin>@<marketplace>
   ```

   The in-session equivalents are `/plugin marketplace add ...` and `/plugin install ...` [S2].
8. **Teams.** Pre-configure marketplaces with `extraKnownMarketplaces` and `enabledPlugins` in settings; restrict sources with `strictKnownMarketplaces` and `blockedMarketplaces`. A project-scope install writes the committed `.claude/settings.json`, and each collaborator still installs on their own machine [S2].
9. **Security posture.** Installed plugins run code with the user's privileges, and hooks, monitors, MCP and LSP servers run outside the sandbox [S2]. List exactly what yours contains (hooks, MCP servers, `bin/` scripts) in the README. Users are told to read `hooks/hooks.json`, `.mcp.json` and every file in `bin/` before installing [S2]. Pin integrity where you can: an `archive` source supports a `sha256`, a `github` source supports `sha` [S2]. Signing: not stated.
10. **Anthropic's directory.** Run `claude plugin validate ./your-plugin --strict --profile directory`. Submit through the portal at `https://claude.ai/directory/manage`; it requires a paid claude.ai plan, and the directory runs a safety scan and a policy review beyond the CLI [S2] [L]. The official marketplace does not take portal submissions [S2]. The submission rules and the pre-submission checklist live on claude.com pages that were not read for this guide.
11. **Other routes.** Share a folder or `.zip` and load it with `--plugin-dir` [S2]. For a product, define the agent in code with the Agent SDK: `description` and `prompt` are required, and programmatic agents override file-based agents of the same name [S9].

**Deliverable.** A tagged release and a marketplace entry.

**Gate.** On a clean machine or profile, the two install commands work and the first README example runs.

---

## Step 14. Launch checklist

Go or no-go. Every item needs evidence, not a statement.

- [ ] **Job.** The spec exists and the non-goals are written. (Step 2)
- [ ] **Routing.** Every positive trigger fires and no negative fires. (Steps 8, 10)
- [ ] **Least privilege.** The tool list is an allowlist, each entry justified. (Step 3)
- [ ] **Enforcement.** Each must-never rule is blocked by a deny rule or hook, and an attempt was refused. (Step 7)
- [ ] **Prompt quality.** The Step 5 review checklist passes. (Step 5)
- [ ] **Progressive disclosure.** `SKILL.md` is under 500 lines and references are one level deep. (Step 6)
- [ ] **Measured.** The eval score meets the threshold and beats the baseline. (Step 10)
- [ ] **Fixture run.** Zero rule violations on the bait fixture. (Step 10)
- [ ] **Bounded.** Turn and spend limits are set and a forced-stop test resumes cleanly. (Step 11)
- [ ] **Observable.** A final report in the fixed format, and a transcript you can read. (Steps 5, 11)
- [ ] **Validated.** `validate --strict` exits 0; with `--profile directory` if you will submit. (Step 9)
- [ ] **Documented.** README, CHANGELOG, LICENSE; a stranger installed it. (Step 12)
- [ ] **Versioned.** A tag exists and matches `plugin.json`. (Step 13)
- [ ] **Honest.** The README lists what was not verified. (Step 12)

---

## Step 15. Operate and improve

**Goal.** Keep it correct as models, tools and your needs change.

**Do.**

1. **Watch real runs.** Use the transcripts and the cost numbers. `--debug` accepts category filters and `--debug-file <path>` writes a log [L]. OpenTelemetry export is available through `CLAUDE_CODE_ENABLE_TELEMETRY=1` and the `OTEL_*` variables; subagent completions are reported with agent type, tool-use count, duration and tokens, and content is redacted unless you opt in [S10]. `/usage` breaks usage down by skill, subagent, plugin and MCP server [S4].
2. **Turn every incident into a case.** A failure becomes an eval case first, then a fix, then a re-run of the whole suite.
3. **Re-baseline on model changes.** Run the suite on each new model. Remove prompt text written for an older model that the new one no longer needs; `/doctor prompt-audit` flags outdated or conflicting instructions in CLAUDE.md-style files [S4].
4. **Fold learned lessons back.** If the agent has `memory:`, review its notes periodically and move the good ones into the tracked references. The tracked files stay the source of truth.
5. **Control change.** Never edit a live prompt without a version bump and a changelog line. For hosted agents, roll out gradually while old and new versions run side by side (the "rainbow deployment" approach) [S13].
6. **Retire cleanly.** Mark deprecated versions in the changelog and keep the old tag.

**Deliverable.** A growing eval suite and a changelog.

**Gate.** No release without a green suite.

---

## Appendix A. Subagent frontmatter reference

Source: the subagents documentation [S1], read on 2026-11-13. Only `name` and `description` are required. Unrecognized fields are ignored without an error.

| Field | Values and meaning | Plugin agents |
| --- | --- | --- |
| `name` | Unique id, at most 256 characters, no `:` | Supported (namespaced as `<plugin>:<name>`) |
| `description` | When Claude should delegate | Supported |
| `tools` | Comma-separated string or YAML list; omitted inherits all; `mcp__server__*` allowed | Supported |
| `disallowedTools` | Denylist, same format | Supported |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit` | Supported |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` | Ignored |
| `maxTurns` | Maximum agentic turns; at the limit the output is partial and resumable | Supported |
| `autoCompactWindow` | Integer 100000 to 1000000 (needs a recent version) | Supported |
| `skills` | Skills to preload; the full content is injected, first 32 names | Supported |
| `mcpServers` | Server names or inline definitions | Ignored |
| `hooks` | Lifecycle hooks scoped to this subagent | Ignored |
| `memory` | `user`, `project` or `local`: a persistent directory | Supported |
| `background` | `true` keeps it in the background | Supported |
| `omitClaudeMd` | `true` skips CLAUDE.md files | Supported |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` | Supported |
| `isolation` | `worktree` only | Supported |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | Supported |
| `initialPrompt` | First turn when the agent runs as the main session agent | Ignored |

Where files load from, highest priority first: managed settings, the `--agents` flag (JSON, session only), `.claude/agents/`, `~/.claude/agents/`, then a plugin's `agents/`. Changes are picked up within seconds; creating the first agent file in a new `agents/` directory needs a restart [S1].

---

## Appendix B. Agent body template

Copy into `agents/<name>.md` after the frontmatter, and fill every angle bracket.

````markdown
You are <role in one sentence>. You take <input> and produce <outputs>, the way <context or precedent>. The playbook is the `<skill>` skill, preloaded: follow its phases in order. Read its reference files when a phase says so.

## Start

1. Take <input> from the prompt. If it is missing or invalid, report `STATUS: BLOCKED` with the reason and stop.
2. If <progress file> exists, this is a resume: read it and continue from the first unfinished phase.
3. <first read or check>.

## Hard rules

1. <A rule a transcript can prove or disprove.>
2. <Next rule.>

## How you work

- You cannot ask questions. Decide with the defaults in the skill, record each decision, and continue.
- Evidence for every claim: a command you ran and its output. Anything not run goes under "Not verified".
- <Budget rule: when to stop adding scope and report partial.>

## Decisions without asking

| Situation | Default |
| --- | --- |
| <ambiguous case> | <what to do> |

## Stop conditions

- BLOCKED when <exact cases>, and say what a human must do.
- PARTIAL when <exact cases>, and name the progress file.

## Report

STATUS: COMPLETE, BLOCKED or PARTIAL
Changed: <fixed shape>
Verified: <commands actually run and their results>
Remaining: <what is not done or not verified>
Risk: <what could still be wrong>
````

---

## Appendix C. Eval case templates

Scaffold with `claude plugin eval init --bare <name>`; the files below show the generated shape [L] extended with fields documented in [S6]. Unknown frontmatter keys in `prompt.md` are errors [S6].

`evals/<case>/prompt.md`:

```markdown
---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

<The user request, exactly as a user would type it.>
```

Documented optional keys: `schema_version`, `name`, `description`, `tags`, `plugins`, `runs` (default 3), `expected_outcome`, `model`, `max_turns` (default 10, maximum 200), `timeout_seconds` (default 300, maximum 3600), `append_system_prompt`, `env` (keys must match `EVAL_[A-Z0-9_]*`) [S6].

`evals/<case>/graders/criteria.md` (an LLM rubric):

```markdown
---
type: llm
weight: 1
---

A successful response <states the observable properties of a correct answer, one per line>.
```

Other grader `type` values documented in [S6]:

| Type | Checks | Key fields |
| --- | --- | --- |
| `regex` | Text in the last message, trace or files | `pattern`, `flags`, `match`, `target` |
| `llm` | A rubric, passing on at least 2 of 3 judge votes | `criteria`, `focus` |
| `tool_used` | That a tool was called (use `tool: Skill` for a trigger check) | `tool`, `input_match`, `min`, `max` |
| `tool_order` | That one call came before another | `before`, `after` |
| `file_exists` | That a file exists, or does not | `path`, `exists` |
| `baseline` | The answer against a reference file | `baseline_file`, `criteria` |

Common grader fields: `weight` (default 1) and `arm` (`with-only` or `both`). A run's score is the weighted fraction of graders passed; a case passes at `--threshold` (default 1.0) [S6].

---

## Appendix D. Command cheat sheet

Flags and subcommands were checked against the `--help` output of the installed Claude Code (2.1.322) on 2026-11-13, unless a source tag says otherwise. Only `plugin init`, `plugin validate` and `plugin eval init --bare` were actually run; commands that call a model (`plugin eval`, `-p`) were not run for this guide.

| Task | Command |
| --- | --- |
| Check the version (evals need 2.1.269 or newer [S6]) | `claude --version` |
| Scaffold a plugin (space-separated components) | `claude plugin init <name> --with agents skills` |
| Load a plugin for one session | `claude --plugin-dir <path>` |
| Reload after edits (in a session) | `/reload-plugins` |
| Validate | `claude plugin validate <path> --strict` |
| Validate for directory submission | `claude plugin validate <path> --strict --profile directory` |
| See components and token cost | `claude plugin details <name>` |
| Scaffold an eval case | `claude plugin eval init --bare <name>` |
| Run evals | `claude plugin eval <path> --trust-plugin --json results.json --threshold 0.8` |
| Run one agent headless | `claude -p --agent <name> --output-format json --max-budget-usd <n> "<task>"` |
| Define agents as JSON for one run | `claude --agents '<json>'` (also a file path with `-p`) [S8] |
| Tag a release | `claude plugin tag --dry-run`, then `claude plugin tag --push` |
| Host and install | `claude plugin marketplace add <owner>/<repo>`, `claude plugin install <plugin>@<marketplace>` [S2] |
| Debug | `claude --debug='<categories>' --debug-file <path>` |
| Minimal scripted mode | `claude --bare -p ...` skips hooks, skills, plugins, MCP and CLAUDE.md [S8] |

---

## Appendix E. Worked example: `repo-modernizer` against this guide

The agent in `agents/repo-modernizer.md` with the skill in `skills/modernize-repo/` was built before this guide existed. Scoring it against the launch checklist shows what the guide would have changed.

| Item | Status | Evidence or gap |
| --- | --- | --- |
| Job and non-goals | Met | One job, with "Not for one feature or one bug fix" in the description |
| Routing tests | Open | The agent is registered and listed, but no positive and negative trigger prompts were run |
| Least privilege | Met | An explicit `tools:` allowlist; MCP access limited to two servers by wildcard |
| Enforcement | Partly | Verified in `settings.json`: 17 deny rules cover push, pull, fetch, remote, sudo, `.env` reads and `git config --global`. There is no `attribution` setting and no hook, so the "no AI attribution in commits" rule and the "never touch the owner's uncommitted files" rule are prompt-only. Next steps: set `"attribution": false` and add a `PreToolUse` hook (matcher `Bash`, `if: Bash(git commit *)`) that exits 2 on an attribution trailer, then test both against a subagent, because the sources do not say the setting applies to subagents |
| Prompt quality | Met | Role, start, hard rules, decisions table, report contract; the procedure lives in the skill |
| Progressive disclosure | Met | A playbook preloaded into the agent, with seven references and templates read on demand |
| Measured against a baseline | Open | No `evals/` directory, so no score and no baseline |
| Fixture run | In progress | A throwaway repository with planted defects and bait (a secret only in history, an uncommitted owner file, a `.env` canary) was built, and the agent is running on it. The outcome is not recorded in this guide yet |
| Bounded | Partly | `maxTurns: 400` and a progress file for resuming; no spend cap and no forced-stop test |
| Observable | Met | A fixed report format; subagent transcripts are written by Claude Code |
| Validated | Met | `claude plugin validate` passes for the agents and skills directories |
| Documented | Partly | A section in the `claude-code` README and the skill's own files; no standalone README or changelog |
| Versioned and installable | Open | Not packaged as a plugin; personal use only |

Open items, in priority order: write 20 eval cases (including trigger and bait cases), add the commit-attribution hook, add a spend cap to any headless use, and package it as a plugin if it is to be shared.

---

## Appendix F. Sources

Read on 2026-11-13. Facts from these pages are tagged in the text. Pages change often: re-read before you rely on a detail.

| Tag | Source |
| --- | --- |
| S1 | Claude Code, subagents: `https://code.claude.com/docs/en/sub-agents` |
| S2 | Claude Code, plugins: `https://code.claude.com/docs/en/plugins`, `.../plugins-reference`, `.../plugin-marketplaces`, `.../plugins/publish`, `.../plugins/security`, `.../plugins/cli-reference` |
| S3 | Claude Code, skills: `https://code.claude.com/docs/en/skills` |
| S4 | Claude Code, best practices: `https://code.claude.com/docs/en/best-practices` |
| S5 | Agent Skills, authoring best practices: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` |
| S6 | Claude Code, plugin evals: `https://code.claude.com/docs/en/plugin-evals` |
| S7 | Claude Code, hooks: `https://code.claude.com/docs/en/hooks` (the SubagentStart and SubagentStop wording was read through a summary: confirm it on the page before coding against it) |
| S8 | Claude Code, headless and CLI reference: `https://code.claude.com/docs/en/headless`, `.../cli-reference` |
| S9 | Agent SDK: `https://code.claude.com/docs/en/agent-sdk/overview`, `.../agent-sdk/subagents` |
| S10 | Claude Code, monitoring usage: `https://code.claude.com/docs/en/monitoring-usage` |
| S11 | Anthropic, "Building effective agents": `https://www.anthropic.com/engineering/building-effective-agents` (a note on the page says some of its tooling has changed since December 2024) |
| S12 | Anthropic, "Writing effective tools for AI agents": `https://www.anthropic.com/engineering/writing-tools-for-agents` |
| S13 | Anthropic, "How we built our multi-agent research system": `https://www.anthropic.com/engineering/multi-agent-research-system` |
| S14 | Anthropic, "Effective context engineering for AI agents": `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents` |
| S15 | Claude Code, permissions, settings and hooks: `https://code.claude.com/docs/en/permissions`, `.../settings-reference`, `.../hooks`. The `attribution` details were read through a summary of the settings reference: confirm them on the page |
| L | The installed Claude Code 2.1.322: `claude --help`, `claude plugin <command> --help`, `claude plugin validate`, `claude plugin eval init --bare` |

Not read, and worth reading before a directory submission: the plugin directory's submission rules and pre-submission checklist on claude.com, the SDK permissions, sessions, cost-tracking and secure-deployment pages, and Anthropic's article on how Managed Agents were built.
