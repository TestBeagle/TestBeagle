# breachsweep report — OWASP Juice Shop (2026-10-11)

Korean version (default): [breachsweep-report.md](breachsweep-report.md)

## Test scope & authorization
- Target: locally running OWASP Juice Shop, container `tb-juice`, http://127.0.0.1:3100 (already started by the coordinator; this run did not start/stop/restart it).
- Authorization: under the user's delegation, the coordinator **approved** this plan (ladder steps 1–5, read-only, 127.0.0.1:3100 only, ≤5 req/s). Juice Shop is an open-source, intentionally-vulnerable training app; the owner of this machine runs it locally with no external integrations. Nothing outside the plan was performed.
- Method: non-destructive, read-only. `curl` GET/OPTIONS, self-registration of my own test accounts A/B via the normal signup API, and cross-account **reads** while holding tokens. No login/auth bypass, no UNION/data extraction, no stored payloads, no writes/deletes to data I did not create.
- Observed vs demonstrated: classes that require an actual exploit (SQLi extraction, XSS, token forgery, `/ftp` file download, admin-role registration) are all placed under "Unverified / out of scope". SOLUTIONS.md and challenge hint data were not used as evidence.

## Environment
- Source: image /juice-shop@5658473 · running build: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · match: yes · build mode: prod
- OS / runtime: macOS (darwin 27.0.0), Docker container `tb-juice`
- Driver: curl (all evidence in this run collected with curl). agent-browser 0.37.0 was available (session var prepared) but every check was API/header-level, so no browser navigation was needed and no agent-browser session was opened.
- Seed/data: accounts I registered — A (id 25, basket 6), B (id 26, basket 7). Existing seed data was only read.

## Summary
- By severity: Critical 0 · High 4 · Medium 0 · Low 4 · Info 0 (report-base rule 9: sensitive-data exposure = High, config observed without demonstrated harm = Low)
- Demonstrated (read-only exploitation): F1 IDOR, F2 BOLA, F4 password hash in JWT. Source-confirmed: F5 hardcoded signing keys. Observed (config, harm not demonstrated): F3 `/ftp` listing, F6 missing CSP, F7 wildcard CORS, F8 other headers.
- Coverage: authZ/IDOR · authN · input validation (ladder 1–2) · secret exposure · headers/transport · client bundle. Items needing an exploit are unverified.

## Findings

### [HIGH] F1. Cross-account read on `/rest/basket/:id` (IDOR)
- Area·kind·confidence: authorization (BOLA/IDOR) · demonstrated · confirmed
- Symptom location: `GET /rest/basket/:id`
- Reproduction: with account A (UserId 25, own basket 6) token, `GET /rest/basket/7` (owned by B) → `HTTP 200`, returns `{"id":7,...,"UserId":26,...}`. The same request with no token returns `UnauthorizedError` (authentication is enforced). Evidence: [evidence/breachsweep/idor-basket-A-reads-7.txt](evidence/breachsweep/idor-basket-A-reads-7.txt)
- Cause location: `server.ts:418` `app.use('/rest/basket/:id', security.isAuthorized())` — requires authentication only, no ownership check. `routes/basket.ts:19` `BasketModel.findOne({ where: { id } })` looks up the path param `id` directly; the ownership comparison at lines 21–24 is only `challengeUtils.solveIf(...)` (marks a challenge) and does **not** deny access. · confirmed (file opened)
- Impact: any authenticated user can read another user's basket (products, coupon) by changing the basket id.
- Fix: in `retrieveBasket`, compare the token's `bid` to the path `id` and return 401/403 on mismatch (promote the current `solveIf` comparison into an access denial).

### [HIGH] F2. `/api/Users` full enumeration and arbitrary-user read (BOLA)
- Area·kind·confidence: authorization (function-level) · demonstrated · confirmed
- Symptom location: `GET /api/Users`, `GET /api/Users/:id`
- Reproduction: with plain customer A token, `GET /api/Users` → `HTTP 200`, returns all 26 users (including admin@juice-sh.op role=admin) with `email`·`role`·`lastLoginIp`. `GET /api/Users/1` → the admin record. With no token → `UnauthorizedError`. Evidence: [evidence/breachsweep/authz-A-lists-all-users.txt](evidence/breachsweep/authz-A-lists-all-users.txt), [evidence/breachsweep/authz-A-reads-user1.txt](evidence/breachsweep/authz-A-reads-user1.txt)
- Cause location: `server.ts:382` `app.get('/api/Users', security.isAuthorized())` and `server.ts:383-384` `app.route('/api/Users/:id').get(security.isAuthorized())` — authentication only, no role/ownership restriction; then `server.ts:500` `finale.initialize(...)` auto-serves the whole User model. (PUT/DELETE are blocked with `denyAll()`, but GET is open.) · confirmed (file opened). Note: the response omits `password`/`totpSecret`, so those fields are not leaked via this route.
- Impact: any authenticated customer can read the full user roster (emails, roles, last-login IPs), enabling enumeration/targeting.
- Fix: add a role check (admin only) or own-record filter to `GET /api/Users`·`/api/Users/:id`; replace the finale auto-exposure with an explicit handler.

### [LOW] F3. Unauthenticated `/ftp` directory listing (observed)
- Area·kind·confidence: file exposure · observed · confirmed (observed response)
- Symptom location: `GET /ftp` (verified at runtime). `/encryptionkeys`, `/support/logs`, `/.well-known`, `/infrastructure` are source-confirmed only — no runtime evidence was saved and the container is stopped, so runtime is unverified.
- Reproduction: `GET /ftp` → directory listing HTML exposing **filenames** as links: `ftp/coupons_2013.md.bak`, `ftp/package.json.bak`, `ftp/package-lock.json.bak`, `ftp/incident-support.kdbx` (KeePass DB), `ftp/announcement_encrypted.md`, `ftp/encrypt.pyc`, `ftp/suspicious_errors.yml` (contents were not read). Evidence: [evidence/breachsweep/ftp-listing.txt](evidence/breachsweep/ftp-listing.txt)
- Cause location: `server.ts:288` `serveIndex('ftp', ...)` (runtime + source confirmed). The same pattern in source at `server.ts:296` `/encryptionkeys`, `server.ts:300` `/support/logs`, `server.ts:292` `/.well-known`, `server.ts:268` `/infrastructure` is config-confirmed but runtime-unverified. · `/ftp` confirmed, others source-config only
- Impact: filenames that look like backups and credential containers are listed without authentication. Contents were not read, so harm is not demonstrated → Low. If file contents were downloadable (or an extension-filter bypass worked), it would become sensitive-data exposure (High) — but that is unverified.
- Fix: disable `serveIndex` directory browsing in production; move `/ftp`·`/encryptionkeys` behind authn/authz or remove the exposure.

### [HIGH] F4. JWT payload embeds the password hash (demonstrated)
- Area·kind·confidence: sensitive data exposure · demonstrated · confirmed
- Symptom location: the JWT body issued by `POST /rest/user/login`
- Reproduction: decoding the payload (base64, unencrypted) of my OWN account A token shows the `data` key containing `password` (a non-empty hex string; the app stores unsalted MD5 per `lib/insecurity.ts:41`) and a `totpSecret` key. `totpSecret` is present as a key but empty: per `routes/login.ts:37-48` this login token is only issued when `totpSecret === ''`, and 2FA users instead get a 401 `tmpToken` (whether a populated 2FA seed ever reaches a token → see Unverified table). By contrast `GET /api/Users/:id` omits both fields → the password-hash leak is specific to the token body. Evidence: [evidence/breachsweep/jwt-embeds-sensitive-fields.txt](evidence/breachsweep/jwt-embeds-sensitive-fields.txt) (token value `<redacted>`)
- Cause location: `routes/login.ts:23-24` builds `{ data: user, bid }` and passes it to `security.authorize(authenticatedUser)`; `lib/insecurity.ts:54` `jwt.sign(user, privateKey, ...)` signs it as-is with no field stripping. · confirmed (file opened)
- Impact: anyone holding the (unencrypted base64) token can read the password MD5 hash (unsalted → crackable). report-base rule 9 "sensitive data exposed" → High.
- Fix: whitelist token claims to a minimal set like `{ id, email, role }`; strip `password`·`totpSecret` from the `authorize()` input.

### [HIGH] F5. Signing/crypto secret keys hardcoded in source (source-confirmed)
- Area·kind·confidence: secret exposure · source-confirmed · confirmed (source opened). Rule 9: a signing private key (sensitive data) exposed → High.
- Symptom location: JWT signing key / HMAC key
- Reproduction: `lib/insecurity.ts:21` holds an RSA private key as a string constant; `lib/insecurity.ts:42` hardcodes the HMAC key `<redacted>`. The matching public key file sits in a source-configured serve-index path (`encryptionkeys/jwt.pub`, F3); runtime exposure is unverified.
- Cause location: `lib/insecurity.ts:21`, `lib/insecurity.ts:42` · confirmed (file opened)
- Impact: the signing key is a fixed constant in public source. **Forging tokens with this key for privilege escalation is an actual exploit → unverified / out of scope.**
- Fix: move keys out of source into env vars / a secret manager; rotate per deployment.

### [LOW] F6. No Content-Security-Policy header (observed)
- Area·kind·confidence: missing security header · observed · confirmed. Rule 9: config observed, no actual XSS/harm demonstrated → Low (best practice).
- Symptom location: all response headers
- Reproduction: `GET /` response has no `Content-Security-Policy`. Evidence: [evidence/breachsweep/headers-root.txt](evidence/breachsweep/headers-root.txt)
- Cause location: `server.ts:186-188` — only `helmet.noSniff()`·`helmet.frameguard()` are applied; `helmet.contentSecurityPolicy()` is not. `server.ts:188` has `helmet.xssFilter()` commented out. · confirmed (file opened)
- Impact: no script-source restriction / inline blocking to mitigate XSS if it occurs.
- Fix: introduce a CSP starting from at least `default-src 'self'`; define a script/style source whitelist.

### [LOW] F7. Overly permissive CORS (`Access-Control-Allow-Origin: *`) (observed)
- Area·kind·confidence: CORS config · observed · confirmed. Rule 9: config observed, and with Bearer-token auth no data theft was demonstrated → Low.
- Symptom location: all responses, including preflight
- Reproduction: both `GET /` and `OPTIONS /rest/products/search` sent with `Origin: https://evil.example` return `Access-Control-Allow-Origin: *` (204). Evidence: [evidence/breachsweep/cors-preflight.txt](evidence/breachsweep/cors-preflight.txt)
- Cause location: `server.ts:182-183` `app.options('*', cors())` / `app.use(cors())` — applied with no origin restriction. · confirmed (file opened)
- Impact: any origin can read responses. Since auth is a Bearer token (not cookies), wildcard CORS alone is not immediate credential theft (proving that is out of scope), but it widens the response-exposure surface.
- Fix: restrict allowed origins to an explicit whitelist.

### [LOW] F8. Other headers: no HSTS / Referrer-Policy, internal path disclosure (observed)
- Area·kind·confidence: security headers / info disclosure · observed · confirmed
- Symptom location: all response headers
- Reproduction: responses lack `Strict-Transport-Security` and `Referrer-Policy`; `X-Recruiting: /#/jobs` is present. Evidence: [evidence/breachsweep/headers-root.txt](evidence/breachsweep/headers-root.txt)
- Cause location: `server.ts:186-188` (helmet defaults not applied), `server.ts:198` `res.append('X-Recruiting', ...)` · confirmed (file opened)
- Impact: **HSTS production impact cannot be established on a local HTTP instance** (only meaningful over HTTPS in deployment). Without Referrer-Policy, the full URL can leak via Referer on outbound navigation. `X-Recruiting` is minor unnecessary info.
- Fix: set `Strict-Transport-Security` at the TLS terminator, `Referrer-Policy: strict-origin-when-cross-origin`, and remove `X-Recruiting` from production responses.

## Observed but not filed as findings (normal / held)
- `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` present (`server.ts:186-187`). Normal.
- `/api/Users` returns `UnauthorizedError` without a token — authentication itself is enforced (the issue is authorization, F2).
- `/rest/products/search?q='` (single quote) → `HTTP 200` `{"status":"success","data":[]}`, no SQL error leakage. (Proving SQLi would need a crafted payload → out of scope.)
- `GET /main.js.map` returns `HTTP 200` but the body is the SPA `index.html` (text/html, 9393B; a nonexistent `/nope.js.map` returns the same). **Not a source-map exposure** — excluded as a false positive.

## Unverified / out of scope
| Item | Reason | How to verify in an authorized environment |
|------|------|------|
| SQL injection (login bypass / search extraction) | login bypass & UNION/extraction forbidden by plan; single quote leaked no error | input-validation test with crafted payloads on a re-seedable staging |
| XSS (reflected/stored) | no stored payloads / script injection performed | place inert markers in search/review inputs, observe reflection/execution |
| JWT forgery / privilege escalation | token manipulation / auth bypass out of scope | sign/verify tokens with the hardcoded key (F5) |
| Populated TOTP seed reaching a token | per `routes/login.ts:37-48` a 2FA user gets a 401 tmpToken instead of this login token, so no 2FA-enabled account token was obtained | complete full login on a 2FA-enabled account, then decode the issued token payload |
| `/ftp` file download / extension-filter bypass | extraction out of scope | `curl /ftp/<file>.bak`, Poison Null Byte, etc. |
| Admin-role self-registration (priv-esc) | privilege-escalation exploit out of scope | pass `role` in signup and check for elevation |
| Rate limiting / brute force | no flooding (≤5 req/s) | measure separately in an authorized load environment |
| Dependency vulns (`npm audit`) | SRC node_modules removed + offline/no-download means no cache | run `npm audit` in a network-permitted environment |

## Evidence index
`docs/examples/juice-shop/evidence/breachsweep/` (tokens/JWTs/cookies/passwords are `<redacted>`):
- `headers-root.txt` — root response headers (F6/F7/F8)
- `idor-basket-A-reads-7.txt` — F1 cross-account basket read
- `authz-A-lists-all-users.txt`, `authz-A-reads-user1.txt` — F2 user enumeration/read
- `jwt-embeds-sensitive-fields.txt` — F4 sensitive fields in token
- `cors-preflight.txt` — F7 preflight
- `ftp-listing.txt` — F3 directory listing
- `register-a.json`/`register-b.json`, `login-a.json`/`login-b.json` (token redacted), `accounts.txt` — accounts A/B setup
- `sqli-errorleak-search-quote.txt` — single-quote observation (no error leak)

bugsweep and a11ysweep run in parallel on the same app; their issues are not duplicated here.
