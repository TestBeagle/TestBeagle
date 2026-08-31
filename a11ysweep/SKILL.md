---
name: a11ysweep
description: Use when asked to audit accessibility or UX polish of a locally runnable app — color contrast, tap-target size, ARIA/labels, keyboard navigation, locale parity, AI-generated UI slop. Triggers on "접근성 점검", "a11y audit", "UX 점검", "대비/탭타깃 확인".
---

# a11ysweep

Plan-gated accessibility and UX audit of a locally running app: contrast, tap targets, labels, keyboard access, locale parity, and AI-built UI slop — reported against WCAG with evidence.

## Phase 0 — Discover (reuse preflight)

Run/reuse `preflight` for targets, run commands, drivers, output location. Reuse any repo a11y tooling found (e.g. touch-target or localization-parity lint scripts).

## Phase 1 — Plan + approval gate (MANDATORY)

Present the screens/routes to audit and the checks per platform; stop until approved. Same capability-keyed gate as bugsweep (plan mode → plan; Codex → post plan, wait).

## Phase 2 — Audit

**Web** (`../drivers-web.md`):
- Inject **axe-core** via `evaluate_script`, run `axe.run` per route, collect violations.
- Contrast: read computed colors, flag body text below WCAG AA (4.5:1; 3:1 for large text).
- Keyboard: walk focus order with repeated Tab; flag traps, invisible focus, unreachable controls.
- Labels: inputs/buttons/icons without an accessible name.

**Mobile** (`../drivers-mobile.md`):
- Tap targets below the platform minimum (iOS 44pt, Android 48dp) — reuse the repo's touch-target check if present.
- Missing accessibility labels (`accessibilityLabel` / `contentDescription`).
- Locale parity: strings present in one language but not another (reuse the repo's localization-parity lint) — capture the same screen in each locale.

**UI slop** (review prompts, not absolute bans — keep intentional, justified design):
- Korean body text below ~14px.
- Default AI-blue/purple palette (e.g. `#3B82F6`) with no brand rationale.
- Uniform 3/4-column grids where rhythm/emphasis would serve the content.
- Box shadows on every surface; extreme gradients the brand doesn't own.

## Phase 3 — Report

Write per `../report-base.md` (Korean default, anti-slop). Per finding: WCAG 기준(있으면) · 위치 · 왜(검증: axe rule / 측정값 / 스크린샷) · 수정 제안 · 확신. Unaudited screens → 검증 불가.

Optionally offer a static re-check runner via `../emit-runner.md`.
