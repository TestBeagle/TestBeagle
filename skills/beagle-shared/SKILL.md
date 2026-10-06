---
name: beagle-shared
description: Internal shared references for the TestBeagle skills (web/mobile drivers, capture-output locations, report skeleton + anti-slop rules, runner emitter, approval gate). Loaded by preflight, bugsweep, breachsweep, a11ysweep, perfsweep, casewright, scriptify, snap, and repro via ../beagle-shared/<file>.md. Not a standalone skill — do not invoke it directly.
user-invocable: false
disable-model-invocation: true
---

# beagle-shared — shared references for the TestBeagle suite

These files are the single source for behavior every TestBeagle skill shares, so it is identical in every runtime. Each skill loads the ones it needs by relative path; none of this is meant to be invoked on its own.

- `drivers-web.md` — web capture & interaction (repo E2E → agent-browser → browser MCP → headless Chrome).
- `drivers-mobile.md` — iOS Simulator (simctl) & Android (adb) capture, interaction, performance, with the hard rules.
- `capture-output.md` — where screenshots, video, and reports go (repo convention first).
- `report-base.md` — report skeleton and anti-slop rules (evidence per claim, 검증 불가 table, confidence labels, Korean default).
- `emit-runner.md` — emit a static, repo-native `.sh` runner from a verified flow.
- `approval-gate.md` — the mandatory stop before any skill launches, seeds, captures, or probes.
