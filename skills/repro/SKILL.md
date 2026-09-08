---
name: repro
description: Use when you want a video that reproduces a flow or an error/bug and saves the clip — a shareable recording of the steps that trigger a problem. Triggers on "오류 영상으로 남겨줘", "버그 재현 영상", "record a repro video", "capture a video of this bug".
---

# repro

Record a **video** of a flow or a bug reproduction and save the clip, so the problem is shareable and documented — not a full QA report, just the recording (plus the exact steps).

## Phase 0 — Discover (reuse preflight, read-only)

Run/reuse `preflight` for targets, run commands, drivers, and the output location. Nail down the exact steps that trigger the flow/error before recording — a repro video is only useful if it actually shows the problem.

## Phase 1 — Plan + approval gate (MANDATORY)

Present the repro: the target, the step-by-step you'll perform, and where the clip lands (`../beagle-shared/capture-output.md`). Then stop per the shared gate in `../beagle-shared/approval-gate.md`.

## Phase 2 — Record

Start recording, perform the steps, stop recording.

- **iOS**: `xcrun simctl io booted recordVideo clip.mov` (`../beagle-shared/drivers-mobile.md`).
- **Android**: `adb shell screenrecord …` → pull → clean up (`../beagle-shared/drivers-mobile.md`).
- **Web**: `agent-browser record start OUT/repro.webm` → perform the steps → `agent-browser record stop` (real video; `.mp4` also works; needs ffmpeg on PATH — see `../beagle-shared/drivers-web.md`). Without agent-browser, claude-in-chrome `gif_creator` produces an animated GIF. Say which you produced (video vs GIF) — don't imply video if it's a GIF.

Capture a couple of extra frames before and after the trigger so the clip reads clearly.

## Phase 3 — Hand over

Save the clip to the output location and write the reproduction steps beside it (what state, what actions, expected vs actual). If the driver couldn't record on a given platform, say so (검증 불가) rather than faking it. Offer the clip + steps; don't auto-commit.
