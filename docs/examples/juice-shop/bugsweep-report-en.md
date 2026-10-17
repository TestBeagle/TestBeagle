# bugsweep report — OWASP Juice Shop (run 2026-10-11 · revised 2026-10-17)

Korean version (default): [bugsweep-report.md](./bugsweep-report.md)

## Environment
- Target: OWASP Juice Shop · http://127.0.0.1:3100 (container `tb-juice`, started and stopped by the coordinator)
- Source: image /juice-shop@5658473 · running build: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · match: yes · build mode: prod
- OS / runtime: macOS 27.0.1 (Darwin 27.0.0) · container Node (bundled in image) · Chrome for Testing (agent-browser bundle)
- Driver: agent-browser 0.37.0
- Seed/data: no seed. Test account self-registered through the normal signup flow (`bugsweep-<timestamp>@example.test`). Browser session closed at teardown.
- Source tracing: the running build ships no source maps → traced by grepping distinctive strings/selectors from the served bundle into `frontend/src`. node_modules removed → library-internal throw sites can't be opened.
- Revision constraint: at the 2026-10-17 revision the container was stopped and the source copy (`scratchpad/src`) had its files removed by tmp cleanup. Every `file:line` below is a line opened during the run. F5 and F6, added in the revision, could not be re-checked, so their causes are inferred.

### Auth-state labels
Login stores the token in both localStorage and a cookie (`frontend/src/app/login/login.component.ts:102`, `:105`). During the run, "logging out" was done with `localStorage.clear()` only, which left the cookie. States are therefore split three ways:
- **A** pre-signup session (no account; genuinely logged out)
- **B** no localStorage token, cookie token still present (mixed). Frontend guards treat it as logged out, but the server's `whoAmI` still returns the account (the recycle form's Requestor shows the account email).
- **C** logged in

### Side effects during the run
Juice Shop is a training app that shows "challenge solved" banners for certain actions. Three appeared without being intended: "Score Board" right after visiting `#/score-board`, then "View Basket" and "Error Handling" before the `#/2fa/enter` capture. Which request in between (`#/recycle`, `#/track-result`) triggered the last two was not recorded (top of score-board.png, 2fa-enter.png, track-result.png).

## Summary
- By severity: Critical 0 · High 0 · Medium 2 · Low 4 · Info 0
- Coverage (unit: the 47 route entries in `app.routing.ts`): ok 31 · issue 10 · not verifiable 6 · total 47. Entries opened in the browser: 42 (ok 31 + issue 10 + last-login-ip 1)
- Flows confirmed by behavior: signup (`POST /api/Users/` 201), login (`POST /rest/user/login` 200, token issued), add-to-basket (`PUT /api/BasketItems/11` 200, Apple Juice quantity incremented), guard blocking (administration · accounting · deluxe-membership → 403 screen). Every other "ok" means render + console only; submit/save actions were not executed.
- Security/accessibility issues are out of scope here. They belong to breachsweep-report / a11ysweep-report.

## Coverage unit
- The unit is an entry in the `routes` array of `frontend/src/app/app.routing.ts`: 45 `path:` entries (nested children included) plus 2 `matcher:` entries (oauthMatcher, tokenMatcher) = 47. Child routes inside lazy-loaded modules (`wallet-web3`, `web3-sandbox`, `bee-haven`) are not counted separately; the module root is counted.
- An entry is judged once a URL it matches has been opened and its screenshot and console checked. Parent entries (`privacy-security`, `chatbot`) match together with their child URLs, and the parent component renders as the shell of the child screen.
- There is no top-level `''` path. `#/` home is served by the `**` wildcard (SearchResultComponent). Row 40 `''` is chatbot's default child.
- Results: **ok** = the screenshot shows the expected content and the console has no [error]/[warn]. **issue** = filed as a finding. **not verifiable** = not opened, or opened without grounds to judge.

## Route coverage
| # | Entry | URL opened | State | Screenshot | Basis | Result |
|---|------|------|------|------|------|------|
| 1 | `administration` | `#/administration` | B, C (non-admin) | administration-nolocaltoken.png, administration-nonadmin.png | guard | ok (403 "You are not allowed to access this page!") |
| 2 | `accounting` | `#/accounting` | B (C: URL only) | accounting-nolocaltoken.png | guard | ok (403) |
| 3 | `about` | `#/about` | A | about.png | render+console | ok |
| 4 | `address/select` | `#/address/select` | C | address-select.png | render+console | ok |
| 5 | `address/saved` | `#/address/saved` | C | address-saved.png | render+console | ok |
| 6 | `address/create` | `#/address/create` | C | address-create.png | render+console | ok (save not run) |
| 7 | `address/edit/:addressId` | — | — | — | — | not verifiable |
| 8 | `delivery-method` | `#/delivery-method` | C | delivery-method.png | render+console | ok |
| 9 | `deluxe-membership` | `#/deluxe-membership` | A, C | deluxe-loggedout.png, deluxe-loggedin.png | guard+render | ok (A: 403 "Please login to view this page.") |
| 10 | `saved-payment-methods` | `#/saved-payment-methods` | C | saved-payment-methods.png | render+console | ok |
| 11 | `basket` | `#/basket` | A, C | basket-loggedout.png, basket-loggedin.png | flow | ok |
| 12 | `order-completion/:id` | — | — | — | — | not verifiable |
| 13 | `contact` | `#/contact` | A | contact.png | render+console | ok (submit not run) |
| 14 | `photo-wall` | `#/photo-wall` | A | photo-wall.png | render+console | issue F5 |
| 15 | `complain` | `#/complain` | A | complain-loggedout.png | render+console | ok (submit not run) |
| 16 | `order-summary` | `#/order-summary` | B | order-summary-nolocaltoken.png | console+network | issue F4 |
| 17 | `order-history` | `#/order-history` | C | order-history.png | render+console | ok (empty state) |
| 18 | `payment/:entity` | `#/payment/shop` | C | payment-shop.png | console | issue F4 |
| 19 | `wallet` | `#/wallet` | C | wallet.png | render+console | ok |
| 20 | `login` | `#/login` | A, C | login.png, login-loggedin.png | flow | ok |
| 21 | `forgot-password` | `#/forgot-password` | A | forgot-password.png | render+console | ok (reset not run) |
| 22 | `recycle` | `#/recycle` | C (A·B console only) | recycle-loggedin.png | console | issue F1 |
| 23 | `register` | `#/register` | A | register.png | flow | ok |
| 24 | `search` | `#/search`, `#/search?q=apple` | C | search-loggedin.png, search-query.png, search-mobile.png | render+console | ok |
| 25 | `hacking-instructor` | `#/hacking-instructor` | B | hacking-instructor.png | render+console | ok (routes to SearchResultComponent) |
| 26 | `score-board` | `#/score-board` | A | score-board.png | render+console | ok |
| 27 | `track-result` | `#/track-result` | A | track-result.png | render | issue F6 |
| 28 | `track-result/new` | `#/track-result/new` | B | track-result-new.png | render | issue F6 |
| 29 | `2fa/enter` | `#/2fa/enter` | A | 2fa-enter.png | render+console | ok |
| 30 | `privacy-security` (parent) | URLs of 31–35 | C | shell in captures 31–35 | render | ok |
| 31 | `privacy-policy` | `#/privacy-security/privacy-policy` | C | privacy-policy.png | render+console | ok |
| 32 | `change-password` | `#/privacy-security/change-password` | C | change-password.png | render+console | ok (change not run) |
| 33 | `two-factor-authentication` | `#/privacy-security/two-factor-authentication` | C | two-factor-auth.png | render+console | issue F2 |
| 34 | `data-export` | `#/privacy-security/data-export` | C | data-export.png | render+console | ok (request not run) |
| 35 | `last-login-ip` | `#/privacy-security/last-login-ip` | C | last-login-ip.png | render | not verifiable |
| 36 | `juicy-nft` | `#/juicy-nft` | A | juicy-nft.png | render+console | ok |
| 37 | `wallet-web3` | `#/wallet-web3` | B | wallet-web3.png | render+console | issue F3 |
| 38 | `web3-sandbox` | `#/web3-sandbox` | B | web3-sandbox.png | render+console | issue F3 |
| 39 | `chatbot` (parent) | `#/chatbot` | C | chatbot.png | render+console | ok |
| 40 | `''` (chatbot default child) | `#/chatbot` | C | chatbot.png | render+console | ok (welcome screen) |
| 41 | `conversation/:id` | — | — | — | — | not verifiable |
| 42 | `bee-haven` | `#/bee-haven` | B | bee-haven.png | render+console | issue F3 |
| 43 | `coding-challenge/:challengeKey` | `#/coding-challenge/scoreBoardChallenge` | C | coding-challenge.png | render+console | ok |
| 44 | `403` | `#/403` | A | 403.png | render+console | ok |
| 45 | `**` | `#/` | A | home.png | render+console | ok |
| 46 | oauthMatcher | — | — | — | — | not verifiable |
| 47 | tokenMatcher | — | — | — | — | not verifiable |

Variants: there are no theme variants. The app's default theme is dark, so the pairs captured with `set media dark/light` came out in the same theme, and no light-theme capture exists (not verifiable). The only mobile-viewport (390x844) capture is one of `#/search` (search-mobile.png, state C).

## Findings

### F3 [Medium] Three web3 routes render a blank screen with no toolbar; `window.ethereum.on` TypeError (no wallet extension)
- Area · kind · confidence: web3 features (sandbox/wallet/faucet) · runtime error + blank screen · symptom confirmed / TypeError cause confirmed / link to the blank screen inferred
- Symptom location: `#/web3-sandbox`, `#/wallet-web3`, `#/bee-haven` (state B). All three screenshots show a grey blank screen with only the snackbar "Please install a Web3 wallet like MetaMask to proceed." and no app toolbar (menu, search, basket). All three log `Cannot read properties of undefined (reading 'on')`.
- Cause location: `frontend/src/app/web3-sandbox/web3-sandbox.component.ts:60`, `frontend/src/app/wallet-web3/wallet-web3.component.ts:54`, `frontend/src/app/faucet/faucet.component.ts:71`. All three call `window.ethereum.on('chainChanged', ...)` in `ngOnInit` with no guard · confirmed (TypeError) · grep + source
  ```ts
  ngOnInit (): void {
    this.handleAuth()
    window.ethereum.on('chainChanged', this.handleChainChanged.bind(this))
  ```
- Why (evidence): in a browser without a wallet extension `window.ethereum` is undefined, so the `.on` call throws and aborts `ngOnInit`. Console evidence: `evidence/bugsweep/web3-sandbox.console.txt`, `wallet-web3.console.txt`, `bee-haven.console.txt`. The blank screen and missing toolbar are confirmed by the screenshots. Whether this TypeError is what removes the toolbar is inferred, since no further source could be read. The run's earlier claim that the body "renders" (based on ~600 chars of DOM text) is withdrawn: nothing is visible on screen. Users can only leave via the browser's back button.
- Fix: guard all three with `if (window.ethereum) { window.ethereum.on(...) }` and, without a wallet, show the notice inside the normal layout with the toolbar.

### F4 [Medium] Entering payment/order-summary without a selected delivery method → `GET /api/Deliverys/null` 400 + unhandled error
- Area · kind · confidence: checkout flow · unhandled HTTP failure · confirmed
- Symptom location: `#/order-summary` (state B), `#/payment/shop` (state C), when `deliveryMethodId` is absent from sessionStorage.
- Cause location: `frontend/src/app/order-summary/order-summary.component.ts:44`, `frontend/src/app/payment/payment.component.ts:143` · confirmed · grep (request URL matches the call site)
  ```ts
  this.deliveryService.getById(sessionStorage.getItem('deliveryMethodId')).subscribe((method) => {
    this.deliveryPrice = method.price
  })
  ```
- Why (evidence): opening either route outside the checkout sequence calls this with `deliveryMethodId` null, producing `GET /api/Deliverys/null` → 400. Reproduced via network log and `curl` (`evidence/bugsweep/order-summary-400.txt`). `subscribe` has no error callback, so it stays as an unhandled console ERROR (`order-summary-nolocaltoken.console.txt`, `payment-shop.console.txt`). order-summary-nolocaltoken.png shows Delivery 0.00.
- Fix: if `deliveryMethodId` is null, skip the request and send the user back to the delivery step; add an error callback to `subscribe`. Same pattern in both files, so fix them together.

### F6 [Low] Opening order tracking without an id shows "Search Results - undefined" and an unreplaced `{{bonus}}`
- Area · kind · confidence: order tracking · wrong display · symptom confirmed / cause inferred
- Symptom location: `#/track-result` (state A), `#/track-result/new` (state B). Both screenshots show the title "Search Results - undefined", "Bonus Points Earned: {{bonus}}", delivery ETA "? Days", and an empty ordered-products table.
- Cause location: `frontend/src/app/track-result/track-result.component.ts:46-47` queries even when the `?id=` query parameter is missing → `routes/trackOrder.ts:21-22` returns a fabricated `{ orderId: id }` for an unknown order → `track-result.component.html:9` puts that orderId (the string "undefined") in the title, and `:79` passes an undefined `results.bonus` to `translateParams`, leaving `{{bonus}}` unreplaced · inferred · source read. The `/rest/track-order/undefined` response was not saved and the stopped container prevents re-checking.
  ```ts
  this.orderId = this.route.snapshot.queryParams.id
  this.trackOrderService.find(this.orderId).subscribe((results) => {
  ```
- Why (evidence): the normal entry point (the track link in order history) adds `?id=`. Opened from the address bar there is no id, and the flow above draws a nonexistent order as a normal result. Evidence: track-result.png, track-result-new.png.
- Fix: when `orderId` is missing, don't query; show an "enter an order number" state. Server side, return 404 for unknown orders instead of a fabricated record.

### F5 [Low] One seeded photo on the photo wall renders as a broken image
- Area · kind · confidence: photo wall · image load failure · symptom confirmed / cause inferred
- Symptom location: `#/photo-wall` (state A). The item captioned "😼 #zatschi #whoneedsfourlegs" shows a broken-image icon (photo-wall.png).
- Cause location: the seed `imagePath` at `data/datacreator.ts:335` contains `#` (`assets/public/images/uploads/ᓚᘏᗢ-#zatschi-#whoneedsfourlegs-1572600969477.jpg`). `frontend/src/app/photo-wall/photo-wall.component.html:16` puts it unencoded into `<img src="{{ image.url }}">` (`photo-wall.component.ts:68` sets `url: memory.imagePath`) · inferred · source read. The browser treats everything after `#` as a fragment and requests `.../uploads/ᓚᘏᗢ-`. A file with the full name does exist in the build output `frontend/dist/frontend/assets/public/images/uploads/`. No network record of the failed image request was saved.
- Why (evidence): the file exists but the screen shows it broken; the `#` in the URL is the only difference found.
- Fix: encode the path segment with `encodeURIComponent` in the template, or strip `#` from filenames when uploads are stored.

### F1 [Low] `#/recycle` logs ngx-translate "Parameter key is required" when localStorage has no token
- Area · kind · confidence: recycle request form · console error · reproduction confirmed / cause inferred
- Symptom location: `#/recycle`. State A 1/1, state B 3/3, state C 0/3 (`evidence/bugsweep/console-isolation.txt`). The run originally said "logged-out only", but state B is still logged in via the cookie, so the condition is "no token in localStorage" (inferred).
- Cause location: `frontend/src/app/recycle/recycle.component.html:21` `<mat-error translate>` · inferred · grep (the only bare `translate` directive on the page)
  ```html
  <mat-error translate>
    {{"MANDATORY_QUANTITY" | translate}}
  </mat-error>
  ```
- Why (evidence): isolating the console per route (`--clear` + reload) shows this error only on `#/recycle`. Line 21 already has a `translate` pipe as its child, yet the element also carries a bare `translate` directive, which we take to receive empty text as its key at first render. There are no source maps and node_modules is removed, so the library throw site wasn't opened. Evidence: `evidence/bugsweep/recycle-translate-error.txt` (state B), `recycle-loggedout.console.txt` (state A). There is no state-A screen capture (see Not verifiable).
- Fix: drop the bare `translate` directive (`<mat-error>`).

### F2 [Low] 2FA setup screen logs angularx-qrcode "qrdata is empty" on load; no QR in the capture
- Area · kind · confidence: two-factor-auth setup · console error · reproduction confirmed
- Symptom location: `#/privacy-security/two-factor-authentication` (state C, setup form of an account without 2FA). Reproduced 3/3. two-factor-auth.png shows the "Scan the QR code" text but no QR image.
- Cause location: `frontend/src/app/two-factor-auth/two-factor-auth.component.html:52-56` `<qrcode [qrdata]="totpUrl" ...>`. `totpUrl` has no initial value (`two-factor-auth.component.ts:58` `public totpUrl?: string`) and is only filled in the setup-API callback (ts:73-78) · confirmed · grep + component source
- Why (evidence): the template binds `totpUrl` without a guard, so the first render gets an empty value and angularx-qrcode logs "Field `qrdata` is empty". Evidence: `evidence/bugsweep/2fa-qrcode-error.txt`, `two-factor-auth.console.txt`. Whether the QR is drawn after the data arrives, and whether setup can be completed, was not checked (not verifiable).
- Fix: wrap `<qrcode>` in `@if (totpUrl)` or use `[qrdata]="totpUrl ?? ''" [allowEmptyString]="true"`.

## Not verifiable
The 6 entries (rows 7, 12, 35, 41, 46, 47) are listed together with checks that are not route entries.

| Item | Reason | Manual check |
|------|------|------|
| #7 `address/edit/:addressId` | needs a saved address id; no address was created | create an address, then open the edit route with its id |
| #12 `order-completion/:id` | needs the id of a paid order | finish checkout (address→delivery→payment), then open the completion screen |
| #35 `last-login-ip` | the screen opened and shows "IP Address 0.0.0.0". The source defining the expected value wasn't opened and the stopped container prevents re-checking | log out, log in again, compare the shown IP with the real client IP |
| #41 `chatbot/conversation/:id` | needs a conversation id; no chatbot conversation was started | start a conversation, then open the generated id |
| #46 oauthMatcher (`#access_token=`) | needs an OAuth redirect fragment; no external IdP | enter via a real OAuth login redirect |
| #47 tokenMatcher | matcher for one obfuscated path; not reachable by normal navigation | construct and open that path |
| 2FA QR rendering and setup completion (#33) | the capture has no QR, and setup completion (password + initial token) was not run. Container stopped | wait for the QR on the setup screen, scan it with an authenticator app, enter the token, save |
| `#/recycle` logged-out screen (#22) | no state-A capture; the state-B capture was byte-identical to state C and was deleted | capture in a session with both cookies and localStorage cleared |
| `#/accounting` logged-in (non-accountant) screen (#2) | URL checked only, no screenshot | open it logged in and confirm the 403 screen |
| Theme variants (light/dark) | the app's default theme is dark, so changing `set media` gave the same screen; no light capture | switch via the app's own theme control, if any, and capture |
| Trigger requests for the "View Basket" and "Error Handling" banners | network for that interval was not saved | on a fresh container, open `#/recycle` and `#/track-result` one at a time while recording network |
| Server/API routes (`server.ts`): `/ftp`, `/support/logs`, `/file-upload`, `/profile`, `/snippets/*`, `/metrics`, `/b2b/v2`, `/dataerasure`, `/redirect`, `/promotion`, `/video`, `/api/*`, `/rest/*` | API/static endpoints outside the coverage unit (`app.routing.ts`). Outside functional (browser-flow) QA; endpoint testing is breachsweep's lane | see breachsweep-report |

## Screenshot/video index
Full mapping in [screenshots/INDEX.md](./screenshots/INDEX.md). No video. register-filled.png (the filled signup form) was deleted because it showed the security-question answer, which is used for password reset (`routes/resetPassword.ts:41`).
