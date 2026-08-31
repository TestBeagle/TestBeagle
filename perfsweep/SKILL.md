---
name: perfsweep
description: Use when asked to test performance of a locally runnable app — Lighthouse, load time, jank, bundle size, low-power/energy use. Triggers on "성능 점검", "Lighthouse", "느린 이유", "번들 크기", "저전력".
---

# perfsweep

Plan-gated performance audit of a locally running app: load, runtime jank, bundle weight, and energy use — measured, not guessed, with numbers tied to a trace.

## Phase 0 — Discover (reuse preflight)

Run/reuse `preflight` for targets, run commands, drivers, output location. Reuse any existing perf budgets or bundle-analysis config in the repo.

## Phase 1 — Plan + approval gate (MANDATORY)

Present the routes/scenarios to measure and the metrics per platform, then stop per the shared gate in `../approval-gate.md`. Note that numbers are dev-build/local, not production figures.

## Phase 2 — Measure

**Web** (`../drivers-web.md`) — with a browser MCP:
- `lighthouse_audit` per key route (performance category) — capture LCP, CLS, TBT, TTI.
- `performance_start_trace` → interact → `performance_stop_trace`; read insights for long tasks and layout thrash.
- Console long-task / excessive re-render warnings after each route.

Without a browser MCP: run Lighthouse from the CLI (`npx lighthouse http://localhost:PORT/route --only-categories=performance --output=json --quiet --chrome-flags="--headless=new"`); trace-based interaction insights need the MCP, so mark them 검증 불가.

- Bundle weight (any driver): run the repo's build + bundle analyzer; flag oversized entries and heavy dependencies.

**Mobile** (`../drivers-mobile.md` — Performance section):
- Cold-start: Android `adb shell am start -W` (read TotalTime); iOS `xctrace`/Instruments where available, else 검증 불가.
- Dropped frames / jank: Android `adb shell dumpsys gfxinfo <pkg>`.
- **Low-power / energy**: idle CPU and continuous work — flag idle animations, polling, always-on computation (Android `dumpsys batterystats` / `top`; iOS Instruments Energy where available). Where the tools at hand don't expose a metric, mark it 검증 불가.

## Phase 3 — Report

Write per `../report-base.md` (Korean default, anti-slop). Per finding: 지표 · 측정값(+기준선/버짓 대비) · 위치 · 왜(검증: trace/Lighthouse 증거) · 수정 제안 · 확신. Measure before recommending — no "optimize X" without a number showing X is the cost. Unmeasured scenarios → 검증 불가.

Optionally offer a static re-measure runner via `../emit-runner.md`.
