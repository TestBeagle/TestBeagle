---
name: casewright
description: Use when asked to generate or write automated test cases for a locally runnable app — turn user flows, routes, or QA findings into reusable tests (e2e, integration, unit, regression) in the repo's own test framework. Triggers on "테스트 케이스 만들어줘", "테스트 작성", "회귀 테스트", "generate tests", "write test cases", "e2e 테스트 생성".
---

# casewright

Turn flows and findings into **reusable automated test cases** in the repo's own test framework, so coverage persists without an agent re-walking the app each time. Complements bugsweep (exploratory QA) and scriptify (a capture runner with no assertions): casewright produces real tests with assertions.

## Phase 0 — Discover (reuse preflight, read-only)

Run/reuse `preflight`. Additionally detect the repo's **existing test framework and conventions** — e.g. Vitest/Jest, Playwright/Cypress/WebdriverIO, XCUITest, Espresso, pytest, Go `testing` — and its test directory, naming, fixtures, and run command. **Reuse what's there; never introduce a new framework or dependency** unless the user explicitly asks. If the repo has no test setup, plan to emit a structured test-case spec (see Phase 2) rather than inventing a stack.

## Phase 1 — Plan + approval gate (MANDATORY)

Present what you'll generate: which flows/routes/findings become test cases, the framework and file locations, and whether any new dev dependency is unavoidable (call it out — it needs approval). Then stop per the shared gate in `../approval-gate.md`.

## Phase 2 — Generate

- Write test cases in the repo's framework, matching its existing patterns (fixtures, helpers, selectors, naming). One clear case per behavior; assert on stable, observable outcomes — not on flaky timing or incidental DOM.
- **Prefer regression tests from verified findings**: each confirmed bugsweep/breachsweep/a11y bug becomes a test that fails on the bug and passes once fixed.
- Cover the approved flows: happy path plus the meaningful edge/error cases, not just one smoke case per screen.
- **No test framework in the repo?** Emit a structured test-case spec instead (a checklist or Gherkin-style `given/when/then` per flow, with expected results) so the cases are captured for whoever wires up a framework later. Say clearly that these are specs, not executable tests.

## Phase 3 — Run, then hand over

Run the generated tests and report real results. Green tests prove they at least execute and pass; for a regression test, show it **fails on the current bug** (before the fix) so it actually guards something — a test that passes whether or not the bug exists guards nothing. A test you didn't run is unverified; say so. Don't assert flaky/time-dependent state. Offer the tests + how to run them; let the maintainer commit them (don't auto-commit).

Report per `../report-base.md` (Korean default, anti-slop): what was generated, where, what it covers, what ran green/red, and what's still uncovered (검증 불가 / 미커버).
