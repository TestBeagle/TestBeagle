# approval-gate — the mandatory stop before any skill acts

Every testbeagle skill presents its plan and **STOPS here**. Do not launch, install, seed, capture, probe, or write anything until the user approves. This file is the single source for the gate — each skill references it so the behavior is identical in every runtime.

## The plan must include

- **Targets** and what you will do to each.
- **Required permissions**: dev servers, simulator/emulator, `adb` — and call out every **destructive** step explicitly (e.g. an Android reinstall that erases app data, or any state-changing security probe).
- **Report language + output location** (`../capture-output.md`).
- **What you will NOT be able to verify**, with the reason (e.g. no browser MCP → capture-only; simctl can't tap).

## Gate on runtime capability (identical outcome everywhere)

- **Plan mode available** (e.g. Claude Code): present the plan through plan mode and request approval that way.
- **No plan mode** (e.g. Codex CLI): post the plan as a normal message ending on its own line with exactly:

  `이 계획대로 진행할까요? (수정/제외할 항목이 있으면 알려주세요)`

  Then wait. Act only after the user replies with **explicit approval**. Silence, an unrelated message, or your own restatement is **not** approval. Apply any requested change to the plan, then re-confirm before acting.

Everything before this gate must be **read-only** (reading files, discovery). Nothing that launches, installs, seeds, captures, or probes may run until approval is given.
