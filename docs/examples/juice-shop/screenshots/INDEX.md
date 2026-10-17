# Screenshot index — bugsweep OWASP Juice Shop (run 2026-10-11 · revised 2026-10-17)

driver: agent-browser 0.37.0 · captures are 1280x633 except `coding-challenge.png`, `order-history.png`, `payment-shop.png`, `search-query.png` (1280x800) and `search-mobile.png` (390x844) · `#/...` hash routes · app default theme is dark (no light captures exist)

State: **A** = pre-signup, genuinely logged out · **B** = localStorage token cleared but auth cookie still present (mixed; not logged out server-side) · **C** = logged in

| File | Route | State | Notes |
|------|------|------|------|
| home.png | `#/` | A | product list |
| search-loggedin.png | `#/search` | C | product list, basket badge 2 (was mislabeled home-dark.png) |
| search-mobile.png | `#/search` | C | viewport 390x844 |
| search-query.png | `#/search?q=apple` | C | 3 results |
| login.png | `#/login` | A | |
| login-loggedin.png | `#/login` | C | login form shown while logged in (was mislabeled login-dark.png) |
| register.png | `#/register` | A | empty form |
| forgot-password.png | `#/forgot-password` | A | |
| contact.png | `#/contact` | A | |
| about.png | `#/about` | A | |
| photo-wall.png | `#/photo-wall` | A | broken image (F5) |
| score-board.png | `#/score-board` | A | "Score Board" challenge banner |
| recycle-loggedin.png | `#/recycle` | C | Requestor shows the test account email |
| track-result.png | `#/track-result` | A | "Search Results - undefined", `{{bonus}}` (F6) |
| track-result-new.png | `#/track-result/new` | B | "Search Results - undefined", `{{bonus}}` (F6) |
| 2fa-enter.png | `#/2fa/enter` | A | three challenge banners |
| 403.png | `#/403` | A | |
| juicy-nft.png | `#/juicy-nft` | A | |
| complain-loggedout.png | `#/complain` | A | |
| hacking-instructor.png | `#/hacking-instructor` | B | product list |
| administration-nolocaltoken.png | `#/administration` | B | 403 (was administration-loggedout.png) |
| administration-nonadmin.png | `#/administration` | C (non-admin) | 403 |
| accounting-nolocaltoken.png | `#/accounting` | B | 403 (was accounting-loggedout.png) |
| basket-loggedout.png | `#/basket` | A | "Your Basket (anonymous)", empty |
| basket-loggedin.png | `#/basket` | C | one row: Apple Juice ×2 (add-to-basket flow) |
| deluxe-loggedout.png | `#/deluxe-membership` | A | 403 "Please login to view this page." |
| deluxe-loggedin.png | `#/deluxe-membership` | C | |
| address-select.png | `#/address/select` | C | |
| address-saved.png | `#/address/saved` | C | |
| address-create.png | `#/address/create` | C | |
| saved-payment-methods.png | `#/saved-payment-methods` | C | |
| wallet.png | `#/wallet` | C | |
| order-history.png | `#/order-history` | C | empty state |
| delivery-method.png | `#/delivery-method` | C | |
| privacy-policy.png | `#/privacy-security/privacy-policy` | C | |
| change-password.png | `#/privacy-security/change-password` | C | |
| two-factor-auth.png | `#/privacy-security/two-factor-authentication` | C | setup form, no QR visible (F2) |
| data-export.png | `#/privacy-security/data-export` | C | |
| last-login-ip.png | `#/privacy-security/last-login-ip` | C | shows 0.0.0.0 (not verifiable) |
| chatbot.png | `#/chatbot` | C | welcome screen |
| coding-challenge.png | `#/coding-challenge/scoreBoardChallenge` | C | |
| order-summary-nolocaltoken.png | `#/order-summary` | B | Delivery 0.00 (F4; was order-summary-loggedout.png) |
| payment-shop.png | `#/payment/shop` | C | (F4) |
| web3-sandbox.png | `#/web3-sandbox` | B | blank screen, no toolbar, MetaMask snackbar (F3) |
| wallet-web3.png | `#/wallet-web3` | B | blank screen, no toolbar, MetaMask snackbar (F3) |
| bee-haven.png | `#/bee-haven` | B | blank screen, no toolbar, MetaMask snackbar (F3) |

Removed:
- register-filled.png — deleted for redaction: it showed the security-question answer, which the app accepts for password reset.
- recycle-loggedout.png — deleted: byte-identical to recycle-loggedin.png and showed the logged-in account. No logged-out recycle capture exists.
- home-dark.png / login-dark.png — renamed (see above); they were not theme variants.

F1 = recycle ngx-translate error (console only) · F2 = 2FA qrcode error · F3 = web3 blank screen / window.ethereum error · F4 = Deliverys/null 400 · F5 = photo-wall broken image · F6 = tracking "undefined" / `{{bonus}}`
