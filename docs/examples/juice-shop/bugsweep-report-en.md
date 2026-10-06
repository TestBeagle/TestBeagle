# bugsweep report — OWASP Juice Shop (2026-09-08)

> English version. The default-language (Korean) report is [`bugsweep-report.md`](./bugsweep-report.md). Same run, same findings.

## Environment
- Target: OWASP Juice Shop (`github.com/juice-shop/juice-shop`) · source commit `1618a61` (2026-08-10) · docker image `bkimminich/juice-shop:latest` = app version 20.2.0
- Run: `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop` · readiness: `GET /rest/admin/application-version` → `{"version":"20.2.0"}` (not an exit code)
- OS / runtime: macOS (darwin 25.6) host, app runs as Node inside the container
- Driver: agent-browser 0.37.0 (interactive) · console/network/error capture used
- Seed/data: docker image default seed. Login account `jim@juice-sh.op` (seed-provided)

## Summary
- By severity: Critical 0 · High 0 · Medium 1 · Low 1 · Info 1
- Coverage: 9/41 routes (9 representative of 41 front-end routes + the logged-in basket) · Unverified 6
- The login flow was actually driven and confirmed to succeed (it is not listed as a finding — behavior confirmed with evidence belongs in the coverage table, not the findings list).

## Route coverage
| Route | State | Variant | Screenshot | Result |
|------|------|------|------|------|
| `/#/` → `/#/search` | logged-out | desktop | `screenshots/home.png` | OK (no console/network error) |
| `/#/search` | logged-out | desktop · mobile 390px | `search.png` · `search-mobile.png` | OK |
| `/#/login` | logged-out | desktop | `login.png` | OK |
| `/#/register` | logged-out | desktop | `register.png` | OK |
| `/#/contact` | logged-out | desktop | `contact.png` | OK |
| `/#/about` | logged-out | desktop | `about.png` | OK |
| `/#/score-board` | logged-out | desktop | `score-board.png` | OK |
| `/#/photo-wall` | logged-out | desktop | `photo-wall.png` | OK |
| `/#/deluxe-membership` | logged-out | desktop | `deluxe.png` | OK |
| `/#/basket` | logged-in (jim) | desktop | `basket-loggedin.png` | OK (login session confirmed) |

Login flow, measured: at `/#/login`, entered and submitted `jim@juice-sh.op` / the seed password → redirected to `/#/search`; `GET /rest/user/whoami` returned `{"user":{"id":2,"email":"jim@juice-sh.op",...}}`, confirming an authenticated session. `basket-loggedin.png` captures the app's own "You successfully solved a challenge: Login Jim" banner together with jim's basket (Raspberry Juice ×2, total 9.98¤), so the evidence is a real logged-in state, not just a rendered screen.

## Findings

### [MEDIUM] Search input is always in the DOM with no accessible label — affects accessibility and automation
- Area · kind · confidence: front end (shared header) · accessibility/markup · confirmed
- Location: the `input[type="text"]` inside the top `mat-toolbar` on every route (the search box; collapsed state has `tabindex="-1"`, `placeholder=""`)
- Why (verification): injected axe-core 4.10.2 via agent-browser and ran `axe.run`. The `label` (critical) rule flagged this input on all three of `/#/search`, `/#/login`, `/#/register`. The collapsed search box renders permanently with no label or placeholder, so a screen reader cannot tell its purpose and a selector cannot distinguish it. Node detail in the a11ysweep report.
- Suggested fix: give the search input an `aria-label` (e.g. "Search products"); when collapsed, remove it from the DOM or apply `aria-hidden` + focus exclusion consistently.

### [LOW] `X-Recruiting` custom header exposed in responses
- Area · kind · confidence: server (HTTP response) · information exposure · confirmed
- Location: all responses. `GET /` carries `X-Recruiting: /#/jobs`
- Why (verification): observed with `curl -D -`. Not a functional defect, but an unnecessary custom header that widens the surface. (Security detail in the breachsweep report.)
- Suggested fix: remove the header in production builds.

### [INFO] No console errors or failed network requests on the 9 audited routes
- Area · kind · confidence: front-end runtime · observation · confirmed
- Location: every route in the coverage table above
- Why (verification): captured `agent-browser console` / `errors` / `network requests` on each route. score-board showed 0 console entries even after a hard reload. Network showed 0 non-2xx/3xx among per-route requests (e.g. 36 requests on the score-board reload were all 2xx/3xx). This is an observation that "only these signals are clean in this scope," not a blanket pass; the Unverified items below are separate.

## Unverified
| Item | Reason | How to check manually |
|------|------|------|
| Registration → actual account-creation submit | state-changing form not submitted (non-destructive) | register for real at `/#/register`, confirm at `/#/login` |
| Payment / order completion (`/#/order-completion`, `/#/payment`) | basket confirmed, but checkout not driven (side effects) | log in as jim and complete checkout |
| 2FA (`/#/2fa/enter`, `/#/two-factor-authentication`) | no 2FA-enabled seed account | log in with a 2FA-registered account |
| Admin screen (`/#/administration`) | no admin session (non-destructive scope) | log in as admin and access |
| Localization (locale variants) | this run captured EN only | switch locale in the language menu and re-capture |
| Light/dark theme variants | the app has a single theme | not applicable |

## Screenshot / video index
`screenshots/` folder. `home.png`=`search.png` (root redirects to search) · `login.png` · `register.png` · `contact.png` · `about.png` · `score-board.png` · `photo-wall.png` · `deluxe.png` · `search-mobile.png` (390×844) · `basket-loggedin.png` (jim logged in).
