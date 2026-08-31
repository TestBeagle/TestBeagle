---
name: scriptify
description: Use when asked to turn a QA or capture flow into a reusable static shell script so it can be re-run without an agent — generate a repo-native `.sh` that launches, seeds, and captures screenshots/video deterministically. Triggers on "정적 스크립트로 만들어줘", "sh 파일로", "에이전트 없이 재실행", "capture script 생성".
---

# scriptify

Freeze a flow the agent already worked out into a committed, repo-native `.sh` runner, so the maintainer can re-run it with no agent and no token cost. This is the mechanism the other skills call in their "offer a runner" step.

## Phase 0 — Discover (reuse preflight)

Run/reuse `preflight` to get the exact launch, seed, and capture commands and the output location. If the flow to script wasn't actually run and verified (by you now, or by a prior bugsweep/a11ysweep/perfsweep run), run it first — a runner is a recording of a working flow, not a guess.

## Phase 1 — Plan + approval gate (MANDATORY)

Present what the script will do (targets, steps, output path, where the file lands) and stop until approved. Same capability-keyed gate as bugsweep (plan mode → plan; Codex → post plan, wait).

## Phase 2 — Emit

Generate the script per `../emit-runner.md`:
- Reuse the repo's existing script style/location if it has one; else portable bash (`set -euo pipefail`, env-parameterized, idempotent, reads bundle id/package from build output, echoes every artifact path).
- Carry the hard rules into the script so they survive without the agent: Android `am start -n` (never `monkey`), uninstall-before-install; iOS verify `BUILD SUCCEEDED` in the log.
- Write it to the repo's `scripts/` (or wherever its current scripts live), `chmod +x`.

## Phase 3 — Verify, then hand over

Run the emitted script once and confirm it produces the expected artifacts. A runner you didn't run is unverified — say so; don't claim it works. Then offer the script + a one-line usage note; let the maintainer commit it (don't auto-commit).
