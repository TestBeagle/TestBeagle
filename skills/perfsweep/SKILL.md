---
name: perfsweep
description: Use when asked to test performance of a locally runnable app — Lighthouse, load time, jank, bundle size, low-power/energy use. Triggers on "성능 점검", "Lighthouse", "느린 이유", "번들 크기", "저전력".
---

# perfsweep

Plan-gated performance audit of a locally running app: load, runtime jank, bundle weight, and energy use — measured, not guessed, with numbers tied to a trace.

## Phase 0 — Discover (reuse preflight)

Run/reuse `../preflight/SKILL.md` for targets, run commands, drivers, output location. Reuse any existing perf budgets or bundle-analysis config in the repo.

## Phase 1 — Plan + approval gate (MANDATORY)

Present the routes/scenarios to measure and the metrics per platform, then stop per the shared gate in `../beagle-shared/approval-gate.md` (if that file is missing, still stop and wait for the user's explicit approval). Record the build mode (dev/prod) — prefer a production build — and label dev numbers as such. Numbers are local, not production figures.

## Phase 2 — Measure

**Web** (`../beagle-shared/drivers-web.md`):
- Lighthouse per key route (performance category) — LCP, CLS, TBT, TTI — at least 3 runs; report the median and min–max, plus Lighthouse version, form factor, and throttling: `npx lighthouse http://localhost:PORT/route --only-categories=performance --output=json --quiet --chrome-flags="--headless=new"` (any driver), or chrome-devtools MCP `lighthouse_audit`.
- Interaction trace: `agent-browser trace start` → interact → `agent-browser trace stop OUT/trace.json`, or chrome-devtools `performance_start_trace` → `performance_stop_trace` → `performance_analyze_insight` (only the MCP summarizes insights for you; with a raw trace, read long tasks from the JSON or mark the insight 검증 불가).
- Live or logged-in pages: `agent-browser vitals --json` for Core Web Vitals on the current page.
- Console long-task / excessive re-render warnings after each route (`agent-browser console`). Capture-only driver → interaction metrics are 검증 불가.

- Bundle weight (any driver): run the repo's build + bundle analyzer; flag oversized entries and heavy dependencies.

**Mobile** (`../beagle-shared/drivers-mobile.md` — Performance section):
- Cold-start: Android `adb shell am start -W` (read TotalTime); iOS `xctrace`/Instruments where available, else 검증 불가.
- Dropped frames / jank: Android `adb shell dumpsys gfxinfo <pkg>`.
- **Low-power / energy**: idle CPU and continuous work — flag idle animations, polling, always-on computation (Android `dumpsys batterystats` / `top`; iOS Instruments Energy where available). Where the tools at hand don't expose a metric, mark it 검증 불가.

## Phase 3 — Report

Write per `../beagle-shared/report-base.md` (Korean default, anti-slop). Per finding: 지표 · 측정값(+기준선/버짓 대비) · 위치 · 왜(검증: trace/Lighthouse 증거) · 수정 제안 · 확신. Measure before recommending — no "optimize X" without a number showing X is the cost. Without a repo budget use: LCP ≤2.5 s good / >4 s poor; CLS ≤0.1 / >0.25; INP ≤200 ms / >500 ms; lab TBT ≤200 ms / >600 ms. Record the poor/needs-improvement class next to the number; assign severity by `../beagle-shared/report-base.md` rule 9 (slow but working is degraded, not broken). Trace each cost to its cause: long task / heavy script → URL → source map or bundle-analyzer module; slow request → handler `file:line`. Unmeasured scenarios → 검증 불가.

Optionally offer a static re-measure runner via `../beagle-shared/emit-runner.md`.
