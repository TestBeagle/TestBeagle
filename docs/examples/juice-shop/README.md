# TestBeagle on OWASP Juice Shop — a real run

This folder is a complete, unedited TestBeagle run against [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) 20.2.0 — a public, intentionally-vulnerable app — recorded on 2026-10-11. Nothing here is a mock-up: every finding cites the command or tool output it came from (saved under [`evidence/`](./evidence/)), names the source line that causes it, and everything the run could not verify is listed as such.

## How it was run

```bash
docker run --rm -d -p 127.0.0.1:3100:3000 bkimminich/juice-shop   # image revision 5658473, app on :3100
# then, in the coding agent:  /beagle  →  bugsweep · a11ysweep · breachsweep
```

- **Source vs build:** cause locations are traced in the source copied out of the same image (`/juice-shop`, revision `5658473`), so every cited `file:line` matches the build that ran. The served frontend has no source maps; frontend causes were traced by grepping distinctive strings and selectors.
- **Driver:** [agent-browser](https://github.com/vercel-labs/agent-browser) 0.37.0 — real navigation, signup/login, and per-route console/error/network capture.
- **Accessibility:** `agent-browser a11y` (bundled axe-core 4.12.1) on the live page, logged out and logged in; WCAG tags and best-practice run separately.
- **Security:** `curl` against the local instance with two self-registered accounts, read-only probes only (no login bypass, no injection payloads beyond a single quote, no writes to data the run didn't create).

## The three reports

| Report | What it covered | Highlight |
|--------|-----------------|-----------|
| bugsweep — [한국어](./bugsweep-report.md) · [English](./bugsweep-report-en.md) | All 47 entries in the frontend route table (42 opened in the browser: 31 OK, 10 with issues; 6 unverified), signup → login → basket | Unhandled `GET /api/Deliverys/null` 400 when order summary opens outside checkout, traced to `order-summary.component.ts:44` |
| a11ysweep — [한국어](./a11ysweep-report.md) · [English](./a11ysweep-report-en.md) | 16 routes, logged out and in, plus keyboard walks | Basket −/+/delete buttons have no accessible name (`purchase-basket.component.html:31,35,51`) |
| breachsweep — [한국어](./breachsweep-report.md) · [English](./breachsweep-report-en.md) | AuthZ with accounts A/B, headers, CORS, exposed directories, JWT contents | Account A reads account B's basket (`routes/basket.ts:19`); any customer lists all users. SQLi, XSS, and JWT forgery left **미검증 / Unverified** |

Reports default to Korean; the agent writes English (or another language you ask for) on request. Both versions above are the same run — identical findings and evidence, different language.

## Why breachsweep didn't claim the famous vulnerabilities

Juice Shop is built to be broken — SQL injection, XSS, and more are there by design. breachsweep reports only what a read-only probe actually proved: the IDOR and user listing were demonstrated with the run's own two accounts, while everything that would need an exploit sits in the 미검증 (unverified) table. Never counting an unexercised path as a pass — or as a finding — is what the whole suite is built around.

Screenshots for every covered route are in [`screenshots/`](./screenshots/) (see its `INDEX.md`).
