---
description: Start a TestBeagle QA run on this repo — preflight, functional QA, security, a11y, performance, test generation, or a static runner.
argument-hint: [preflight|qa|security|a11y|perf|tests|script]
---

# /beagle

Let the QA beagle loose on this repo. The user invoked `/beagle` with:

```
$ARGUMENTS
```

Pick the matching TestBeagle skill and follow its `SKILL.md` exactly. **Every skill is plan-gated** — discover, present the plan, and wait for the user's approval before launching, seeding, capturing, or probing anything (see `approval-gate`).

Route by the argument (case-insensitive):

- **empty**, `qa`, `full` → run **preflight** first, then **bugsweep** (full-path functional QA + screenshots/video).
- `preflight`, `env` → **preflight** only (can this repo be tested locally, and how).
- `security`, `sec`, `pentest` → **breachsweep** (owned/authorized app, local, non-destructive).
- `a11y`, `accessibility`, `ux` → **a11ysweep**.
- `perf`, `performance`, `lighthouse` → **perfsweep**.
- `tests`, `testcases`, `cases` → **casewright**.
- `script`, `runner` → **scriptify**.
- `snap`, `screenshots`, `shots` → **snap** (screenshot every screen → images, no analysis).
- `repro`, `video`, `record` → **repro** (record a video reproducing a flow or error).

If the argument doesn't match, run **preflight**, then show what TestBeagle can test on this repo and ask which to run. Reuse the repo's existing tooling; report in Korean by default per `report-base`.
