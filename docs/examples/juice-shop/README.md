# TestBeagle on OWASP Juice Shop — a real run

This folder is a complete, unedited TestBeagle run against [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) 20.2.0 — a public, intentionally-vulnerable app — recorded on 2026-09-08. Nothing here is a mock-up: every finding cites the command or tool output it came from, and everything the run could not verify is listed as such.

## How it was run

```bash
docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop   # app on :3000
# then, in the coding agent:  /beagle  →  preflight → bugsweep → a11ysweep → breachsweep
```

- **Driver:** [agent-browser](https://github.com/vercel-labs/agent-browser) 0.37.0 — real navigation, interaction, and per-route console/error/network capture. No browser MCP was connected; the interactive path still worked, which is the point.
- **Accessibility:** axe-core 4.10.2 injected into the live page (Juice Shop has no CSP, so injection succeeded).
- **Security:** non-destructive `curl` GET and header inspection only. No injection, no data changes.

## The three reports

| Report | What it found | Highlight |
|--------|---------------|-----------|
| bugsweep — [한국어](./bugsweep-report.md) · [English](./bugsweep-report-en.md) | Functional QA across 9 routes + a real login flow | Login as `jim` verified via `whoami` API and the app's own challenge banner; no console errors or failed requests on the audited routes |
| a11ysweep — [한국어](./a11ysweep-report.md) · [English](./a11ysweep-report-en.md) | axe-core on 3 routes | 1 critical (form input with no label), landmark/region issues, redundant alt text — each with the exact node |
| breachsweep — [한국어](./breachsweep-report.md) · [English](./breachsweep-report-en.md) | Non-destructive config-level checks | `/ftp` directory listing exposed; missing CSP/HSTS/Referrer-Policy; permissive CORS. SQLi/XSS/IDOR classes left in **미검증 / Unverified** because confirming them non-destructively wasn't possible |

Reports default to Korean; the agent writes English (or another language you ask for) on request. Both versions above are the same run — identical findings and evidence, different language — so you can see exactly what a localized report reads like.

## Why breachsweep refused to claim the famous vulnerabilities

Juice Shop is built to be broken — SQL injection, XSS, and IDOR are all there by design. A tool that "found" them here would be cheating. breachsweep only reports what a read-only GET actually proves, and puts every exploit-requiring class in its 미검증 (unverified) table. That discipline — never counting an unexercised path as a pass — is what the whole suite is built around.

Screenshots for every route are in [`screenshots/`](./screenshots/).
