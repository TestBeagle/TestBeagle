---
name: perfsweep
description: Use when asked to test performance of a locally runnable app — Lighthouse, load time, jank, bundle size, low-power/energy use. Triggers on "성능 점검", "Lighthouse", "느린 이유", "번들 크기", "저전력".
---

# perfsweep

Plan-gated performance audit of a locally running app: load, runtime jank, bundle weight, and energy use — measured, not guessed, with numbers tied to a trace.

## Phase 0 — Discover (reuse preflight)

Run/reuse `preflight` for targets, run commands, drivers, output location. Reuse any existing perf budgets or bundle-analysis config in the repo.

## Phase 1 — Plan + approval gate (MANDATORY)

Present the routes/scenarios to measure and the metrics per platform; stop until approved. Same capability-keyed gate as bugsweep (plan mode → plan; Codex → post plan, wait). Note that numbers are dev-build/local and not production figures.

## Phase 2 — Measure

**Web** (`../drivers-web.md`):
- `lighthouse_audit` per key route (performance category) — capture LCP, CLS, TBT, TTI.
- `performance_start_trace` → interact → `performance_stop_trace`; read insights for long tasks and layout thrash.
- Bundle weight: run the repo's build + any bundle analyzer; flag oversized entries and heavy dependencies.
- Console long-task / excessive re-render warnings after each route.

**Mobile** (`../drivers-mobile.md`):
- Cold-start time (launch → first meaningful frame).
- Dropped frames / jank during scroll and transitions.
- **Low-power / energy**: idle CPU and continuous work — flag idle animations, polling, or always-on computation that a low-power app shouldn't have.

## Phase 3 — Report

Write per `../report-base.md` (Korean default, anti-slop). Per finding: 지표 · 측정값(+기준선/버짓 대비) · 위치 · 왜(검증: trace/Lighthouse 증거) · 수정 제안 · 확신. Measure before recommending — no "optimize X" without a number showing X is the cost. Unmeasured scenarios → 검증 불가.

Optionally offer a static re-measure runner via `../emit-runner.md`.
