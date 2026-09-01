---
name: breachsweep
description: Use when asked to security-test, pentest, or find vulnerabilities in a locally runnable app you own — auth/authorization (IDOR), input validation (injection), secret exposure, security headers, insecure cookies/CORS. Triggers on "보안 점검", "취약점 찾아줘", "security audit", "pentest my app".
---

# breachsweep

Plan-gated, non-destructive security testing of an app **you own or are authorized to test**, against a **local** instance. Finds real, fixable issues with reproduction evidence — it is not an attack tool.

## Hard rules (read first — non-negotiable)

- **Scope**: only apps the user owns or is explicitly authorized to test. If ownership/authorization is unclear, ask and stop.
- **Local only**: test a local instance. Never production, never third-party services.
- **Isolated**: before probing, confirm the local instance's external integrations (email, payment, storage, webhooks, push) are sandboxed or disconnected from production/third parties. If you can't confirm, treat those paths as out of scope.
- **Non-destructive by default**: no deletion, no mutation of existing or other-user data, no DoS, no request floods. Read and detect. (Provisioning your own test accounts through the app's normal signup/seed flow is setup, not an attack — that's allowed.) Any state-changing check needs explicit user approval and an isolated, re-seedable environment.
- **Report to fix, not to weaponize**: give the minimum reproduction plus the remediation. Do not write a full weaponized exploit chain.
- **Unverified ≠ safe**: what you couldn't test is "미검증", never "안전".

## Phase 0 — Discover (reuse preflight)

Run/reuse `preflight`. Additionally map: routes/endpoints, the auth middleware, session/token handling, and secret handling. Reuse the repo's own `npm audit` / security CI if present.

## Phase 1 — Plan + approval gate (MANDATORY)

Present, and stop per the shared gate in `../approval-gate.md`, a plan that states:
- **Authorized targets**: exact host(s)/base URL(s) — a local instance only.
- **Allowed methods and account/data scope**, plus a **request-rate ceiling** (no floods).
- **Test categories** to run and what's **out of scope**.
- The **non-destructive guarantee**.
- **Authorization**: the user must personally confirm they own or are authorized to test these targets. Do not proceed on an agent-written assumption — the user affirms it, or you stop.

## Phase 2 — Launch

Local instance only. Seed multiple accounts (A/B) so authorization isolation can be tested.

## Phase 3 — Non-destructive checks

- **AuthZ / IDOR**: with accounts A and B, try to **read** B's objects by id/reference as A (read-only by default). A state-changing authz check (write/delete as the wrong user) runs only if separately approved, against re-seedable data.
- **AuthN**: hit protected endpoints with no/expired/reused session or token.
- **Input validation**: probe SQLi / XSS / path-traversal with **safe, non-destructive** payloads; observe reflection, errors, and error verbosity.
- **Secret exposure**: secrets in responses, source maps, verbose error pages, debug endpoints.
- **Headers / transport**: CSP, HSTS, cookie flags (HttpOnly/Secure/SameSite), CORS misconfiguration.
- **Client**: hardcoded secrets in web JS / mobile bundles; insecure local storage.
- **Dependencies**: run the repo's own audit tool; don't reinvent.

## Phase 4 — Report

Write per `../report-base.md` (Korean default, anti-slop). Header includes **테스트 범위 및 인가**. Per finding: 취약점 유형 · 위치(엔드포인트/파일) · 재현(요청·응답 증거) · 영향 · 수정 제안 · 확신(확실/추정). Close with 미검증/범위 외.

Optionally offer a static re-check runner via `../emit-runner.md`.
