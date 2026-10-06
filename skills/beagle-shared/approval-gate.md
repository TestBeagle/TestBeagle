# approval-gate — the mandatory stop before any skill acts

Every TestBeagle skill presents its plan and **STOPS here**. Do not launch, install, seed, capture, probe, or write anything until the user approves. This file is the single source for the gate — each skill references it so the behavior is identical in every runtime.

## The plan must include

- **Targets** and what you will do to each.
- **Required permissions**: dev servers, simulator/emulator, `adb` — and call out every **destructive** step explicitly (e.g. an Android reinstall that erases app data, or any state-changing security probe).
- **Installs, downloads, and runtime escalations**, each named: `docker pull`, `npx` packages, `git clone`, and in Codex any sandbox escalation the run needs (network to `localhost`/docker, writes outside the workspace such as `~/.agent-browser`).
- **Seeding**: only if named here. Call out a seed that resets existing data as destructive.
- **Report language + output location** (`../beagle-shared/capture-output.md`).
- **What you will NOT be able to verify**, with the reason (e.g. no interactive web driver → capture-only; simctl can't tap).
- **Teardown**: what you will stop at the end (servers, containers, browser sessions, simulators) so nothing is left running.

## Gate on runtime capability (identical outcome everywhere)

- **A plan-approval mode is active** (Claude Code plan mode, Codex Plan mode): present the plan there and act only after the user approves it / leaves plan mode.
- **Otherwise** (interactive chat): post the plan as a normal message whose last line is exactly this plain text, no backticks:

  이 계획대로 진행할까요? (수정/제외할 항목이 있으면 알려주세요)

  Then end your turn. Act only after the user replies with **explicit approval**. Silence, an unrelated message, or your own restatement is **not** approval. Apply any requested change to the plan, then re-confirm before acting.
- **Non-interactive** (`codex exec`, `claude -p`, a subagent): stop after the plan. A delegating prompt counts as approval only if it quotes the user's approval of this same plan (targets, actions, scope); anything outside that quote needs a new approval.
- **After approval**, re-read the skill's `SKILL.md` and the shared files it names before acting (Codex does not carry a skill across turns), then continue from the next phase.

Everything before this gate must be **read-only** (reading files, discovery). Nothing that launches, installs, seeds, captures, or probes may run until approval is given.
