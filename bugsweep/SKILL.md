---
name: bugsweep
description: Use when asked to QA an app end to end, run a full-path / 전체 경로 / 전수 QA, capture screenshots of every screen, or verify all user flows (signup, login, every feature) of a locally runnable web, iOS, Android, API, or monorepo project. Triggers on "전수 QA", "모든 화면 캡쳐", "직접 써보고 버그 찾아줘", "full QA pass".
---

# bugsweep

Plan-gated, full-path functional QA: run the app locally, walk every user path from signup/login through every feature, capture each screen, exercise the flows, and report with evidence. Never claims a pass it didn't verify.

## Phase 0 — Discover (reuse preflight)

Run `preflight` (or reuse its report). Get: targets, run commands, readiness method, seed/review tooling, output location, drivers. If a target isn't locally testable, say so and don't fake it.

## Phase 1 — Route map + approval gate (MANDATORY — stop here)

Build the full route map and present it; **launch/seed/capture nothing until the user approves.** The map lists, for every path from signup/login onward:

- **경로 + 상태**: logged-out/in, empty/populated.
- **변형**: dark mode, locales — whatever the app supports.
- **드라이버** per route (`../drivers-web.md` / `../drivers-mobile.md`).
- **검증 불가 예정** + 이유 (e.g. simctl can't tap; no browser MCP → capture-only).
- **필요 권한** (dev servers, simulator/emulator, adb) and **보고서 언어·출력 위치** (`../capture-output.md`).

Gate wording, keyed on runtime capability so it works identically everywhere:
- If the runtime has a **plan mode** (e.g. Claude Code): present the route map as the plan and request approval through it.
- Otherwise (e.g. **Codex CLI**): post the route map as a message ending exactly with `이 QA 계획대로 진행할까요? (수정/제외할 경로가 있으면 알려주세요)` and wait. Proceed only on explicit approval; apply requested edits to the map first.

## Phase 2 — Launch

Start services with the discovered commands. Confirm readiness by **evidence** (poll the health endpoint; grep the build log for the success marker) — never by exit code alone. Run the seed script if one exists.

## Phase 3 — Capture & QA every route

- Static screens: prefer the repo's native capture scripts / review-mode deep links; else drive the real UI.
- Flows: actually perform signup, login, navigation, CRUD.
- Web: after **every** route, check `list_console_messages` and `list_network_requests` — errors are findings.
- Capture every screen × state × variant in the approved map (screenshots, and video for flows where useful).

## Phase 4 — Report

Write per `../report-base.md` (Korean default, anti-slop rules enforced). Finding fields: the common block plus, per finding, the exact reproduction and the console/network/screenshot evidence. Everything you couldn't exercise goes in 검증 불가.

## Phase 5 — Offer a static runner

Offer to freeze the capture flow into a repo-native `.sh` (via `../emit-runner.md`, the `scriptify` mechanism) so future runs need no agent. Don't auto-commit — offer it.

## Hard rules

- Android: launch with `am start -n`, **never `adb monkey`** (it clears the rotation lock). Uninstall before install — never `install -r` (stale build).
- iOS: a build wrapper's exit 0 is meaningless — confirm `BUILD SUCCEEDED` in the log.
- Any tap/flow/state you can't verify goes in 검증 불가 with the reason. Never silently skip, never fake a pass.
