# breachsweep report — OWASP Juice Shop (2026-09-08)

> English version. The default-language (Korean) report is [`breachsweep-report.md`](./breachsweep-report.md). Same run, same findings.

## Scope and authorization
- Target: a locally-run OWASP Juice Shop 20.2.0 (`docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop`). Public OSS, deliberately built to be vulnerable for training, so public testing is fine.
- Method: **non-destructive, read-only**. Only `curl` GET and observation of static headers/responses. No injection, data change, deletion, mass requests, or auth-bypass attempts.
- Important framing: Juice Shop has SQLi, XSS, IDOR and more planted **by design**. This report does not claim to have "found" them. Only **configuration-level exposures** that a non-destructive GET leaves evidence for are reported as findings; every vulnerability class that requires an actual attack is left under "Unverified / out of scope." That is the breachsweep principle.

## Summary
- By severity: High 1 · Medium 3 · Low 2 · Info 0
- Evidence: all reproducible with a `curl` GET (header or body). Confidence is "confirmed" throughout (the observed response as-is).

## Findings

### [HIGH] `/ftp` directory listing exposed without authentication
- Type · location · confidence: sensitive-file exposure · `GET /ftp` · confirmed
- Reproduction: `curl -s http://localhost:3000/ftp` → returns directory-listing HTML. Links exposed include `ftp/coupons_2013.md.bak`, `ftp/package.json.bak`, `ftp/package-lock.json.bak`, `ftp/incident-support.kdbx` (a KeePass DB), `ftp/announcement_encrypted.md`, `ftp/encrypt.pyc`, `ftp/eastere.gg`.
- Impact: a listing of backup files and what looks like a credential container is plainly visible. Whether each file is actually downloadable, and any extension filter, is outside this non-destructive observation (see Unverified).
- Suggested fix: disable directory listing on the static-file path; move `/ftp` behind authentication/authorization or remove the exposure.

### [MEDIUM] No Content-Security-Policy header
- Type · location · confidence: missing security header · all responses · confirmed
- Reproduction: `curl -s -D - http://localhost:3000/` shows no `Content-Security-Policy` in the response headers. Injecting axe-core from an external CDN (`cdnjs.cloudflare.com`) into the page actually succeeded (a11ysweep run log), which demonstrates there is no script-origin restriction.
- Impact: no mitigation if an XSS occurs. Arbitrary external script loads and inline execution are not blocked.
- Suggested fix: introduce a CSP starting from at least `default-src 'self'`, and define an inline/external script allowlist.

### [MEDIUM] Overly permissive CORS (`Access-Control-Allow-Origin: *`)
- Type · location · confidence: CORS config · all responses · confirmed
- Reproduction: `GET /` response header `Access-Control-Allow-Origin: *`. The server code also applies `app.use(cors())` with no restriction (`server.ts`).
- Impact: any origin can read responses. If auth is token-based rather than cookie-based this is not an immediate credential leak, but it widens the API-response exposure surface.
- Suggested fix: restrict allowed origins to an explicit allowlist.

### [MEDIUM] No HSTS (`Strict-Transport-Security`) header
- Type · location · confidence: missing security header · all responses · confirmed
- Reproduction: no `Strict-Transport-Security` in the response headers.
- Impact: no HTTPS enforcement, risking downgrade / man-in-the-middle. (Local is HTTP, but it is a problem if shipped as-is to production.)
- Suggested fix: set `Strict-Transport-Security: max-age=31536000; includeSubDomains` at the TLS terminator.

### [LOW] No `Referrer-Policy` header
- Type · location · confidence: missing security header · all responses · confirmed
- Reproduction: no `Referrer-Policy` in the response headers.
- Impact: the full URL can leak in the Referer on outbound navigation.
- Suggested fix: set `Referrer-Policy: strict-origin-when-cross-origin`.

### [LOW] `X-Recruiting` custom header leaks an internal path
- Type · location · confidence: information exposure · all responses · confirmed
- Reproduction: `GET /` header `X-Recruiting: /#/jobs`.
- Impact: minor but unnecessary. Remove it to reduce surface.
- Suggested fix: remove it from production responses.

## Observed but not raised as findings (OK / judgment withheld)
- `helmet.noSniff()` / `helmet.frameguard()` confirmed applied: responses carry `X-Content-Type-Options: nosniff` and `X-Frame-Options: SAMEORIGIN` (confirmed). OK.
- Error-response stack exposure: `GET /rest/products/<invalid>/reviews` and `GET /rest/track-order/%27` both returned well-formed JSON (`{"status":"success",...}`) with no stack trace leaked (confirmed). OK for these endpoints only.
- `/.well-known/security.txt`: `200`. Present.

## Unverified / out of scope (not run under the non-destructive principle — NOT "OK")
| Item | Reason | How to check (in an authorized environment) |
|------|------|------|
| SQL injection (login bypass etc.) | payload injection is potentially destructive → not run | test the login form with `' OR 1=1--`-style input on authorized staging |
| XSS (reflected/stored) | script injection not run | submit a `<script>` payload in search/review inputs and observe execution |
| IDOR / access control (`/api/Users`, basket, order) | cross-user resource access not attempted | compare mutual resource-ID access with two authorized accounts |
| Actual `/ftp` file download / extension-filter bypass | download/bypass out of scope | `curl /ftp/<file>.bak`, Poison Null Byte, etc. |
| JWT forgery/tampering, admin privilege escalation | token manipulation not run | test token alg/signature verification |
| Bot-defense / rate limiting | mass-request prohibition | measure separately in an authorized load environment |

## Screenshots / evidence
Header and endpoint evidence is immediately reproducible with the commands above. Screen evidence is in the bugsweep report's `screenshots/`.
