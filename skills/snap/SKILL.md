---
name: snap
description: Use when you just want screenshots of every screen saved as image files — capture all screens/states/variants of a locally runnable app, no QA analysis, no findings, just the pictures. Triggers on "스크린샷 다 찍어줘", "모든 화면 캡쳐해서 저장", "capture all screens", "screenshot everything".
---

# snap

Capture-only: walk every screen and save the images. No interaction QA, no bug analysis, no verdict — just the screenshots (for a design review, changelog, docs, or a before/after diff). For a full QA pass with findings, use **bugsweep** instead.

## Phase 0 — Discover (reuse preflight, read-only)

Run/reuse `preflight` for targets, run commands, drivers, and the output location. Prefer the repo's native capture scripts / review-mode deep links if it has them.

## Phase 1 — Plan + approval gate (MANDATORY)

Present the shot list — screens/routes × states (logged-out/in, empty/populated) × variants (dark mode, locales) — and the output folder (`../capture-output.md`). Then stop per the shared gate in `../approval-gate.md`.

## Phase 2 — Launch & capture

Start the app (readiness by evidence; seed if a script exists). Capture every screen × state × variant with the driver's screenshot commands (`../drivers-web.md` / `../drivers-mobile.md`). Name files `route[-state][-locale][-appearance].png` so the set is scannable and re-runs diff cleanly.

## Phase 3 — Hand over

Write a short index (filename → screen/state/variant) into the output location; note anything that couldn't be reached (검증 불가) with the reason. Offer the images; don't auto-commit. If you'll want to re-capture without an agent later, offer **scriptify** to freeze this into a `.sh`.
