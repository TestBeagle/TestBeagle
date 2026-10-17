# a11ysweep report — OWASP Juice Shop (2026-10-11)

> English version. The default-language (Korean) report is [`a11ysweep-report.md`](./a11ysweep-report.md). Same run, same findings.

## Environment
- Target: OWASP Juice Shop, local container `tb-juice` · `http://127.0.0.1:3100`
- Source: image /juice-shop@5658473 · Running build: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · Match: yes · Build mode: prod
- Cause locations are relative to the repo root (`frontend/src/app/...`), checked against a read-only copy extracted from the image.
- OS: macOS (Darwin 27.0.0)
- Driver: agent-browser 0.37.0 · axe-core 4.12.1 (bundled with agent-browser, `agent-browser a11y`)
- axe runs: on every route, `agent-browser a11y --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa --json`, then `--tags best-practice --json` as a separate run. Best-practice rules carry no WCAG criterion.
- Seed/data: no seed. Logged in with an account created through the normal signup screen, `a11y-1791729257@example.test` (confirmed: `/rest/user/whoami` returned that email). To audit a populated basket, 2 items (Apple Juice, Apple Pomace) were added to this account's basket. bugsweep and breachsweep ran against the same instance at the same time; the challenge-solved notifications visible on screen came from those runs.
- Severity follows report-base rule 9 (impact on the user); axe's raw impact is quoted separately.

## Summary
- By severity: Critical 0 · High 1 · Medium 8 · Low 8 · Info 0
- Coverage: 16/45 routes audited (7 logged out, 9 logged in) · 29 out of scope · unverified items in the table below
- Keyboard walk: `/#/login`, `/#/search` (product list)

## Route coverage
The route inventory is the 45 `path:` entries in `frontend/src/app/app.routing.ts` (child routes and `**` included).

| Route | State | axe WCAG rules violated | axe best-practice rules violated | Evidence | Result |
|------|------|------|------|------|------|
| `/#/search` | logged out, first visit (welcome dialog and cookie banner open) | color-contrast | aria-dialog-name | [wcag](./evidence/a11ysweep/home-welcome-wcag.json) · [bp](./evidence/a11ysweep/home-welcome-bp.json) · [png](./evidence/a11ysweep/home-welcome.png) | issue |
| `/#/search` | logged out, banners dismissed | color-contrast, label | aria-allowed-role, image-redundant-alt, landmark-unique, region | [wcag](./evidence/a11ysweep/home-wcag.json) · [bp](./evidence/a11ysweep/home-bp.json) | issue |
| `/#/search` | logged in | color-contrast, label | same as above | [wcag](./evidence/a11ysweep/search-loggedin-wcag.json) · [bp](./evidence/a11ysweep/search-loggedin-bp.json) | issue |
| `/#/login` | logged out | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/login-wcag.json) · [bp](./evidence/a11ysweep/login-bp.json) | issue |
| `/#/register` | logged out | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/register-wcag.json) · [bp](./evidence/a11ysweep/register-bp.json) | issue |
| `/#/forgot-password` | logged out | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/forgot-password-wcag.json) · [bp](./evidence/a11ysweep/forgot-password-bp.json) | issue |
| `/#/contact` | logged out | label ×2 | image-redundant-alt, region | [wcag](./evidence/a11ysweep/contact-wcag.json) · [bp](./evidence/a11ysweep/contact-bp.json) | issue |
| `/#/about` | logged out | image-alt, label, link-in-text-block, scrollable-region-focusable | image-redundant-alt, region | [wcag](./evidence/a11ysweep/about-wcag.json) · [bp](./evidence/a11ysweep/about-bp.json) | issue |
| `/#/photo-wall` | logged out | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/photo-wall-wcag.json) · [bp](./evidence/a11ysweep/photo-wall-bp.json) | issue |
| `/#/basket` | logged in, empty | aria-required-children, color-contrast, label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/basket-loggedin-wcag.json) · [bp](./evidence/a11ysweep/basket-loggedin-bp.json) | issue |
| `/#/basket` | logged in, populated | aria-required-children, button-name, color-contrast, label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/basket-populated-loggedin-wcag.json) · [bp](./evidence/a11ysweep/basket-populated-loggedin-bp.json) · [png](./evidence/a11ysweep/basket-heading-contrast.png) | issue |
| `/#/address/saved` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/address-saved-loggedin-wcag.json) · [bp](./evidence/a11ysweep/address-saved-loggedin-bp.json) | issue |
| `/#/address/create` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/address-create-loggedin-wcag.json) · [bp](./evidence/a11ysweep/address-create-loggedin-bp.json) | issue |
| `/#/order-history` | logged in, no orders | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/order-history-loggedin-wcag.json) · [bp](./evidence/a11ysweep/order-history-loggedin-bp.json) | issue |
| `/#/saved-payment-methods` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/saved-payment-methods-loggedin-wcag.json) · [bp](./evidence/a11ysweep/saved-payment-methods-loggedin-bp.json) | issue |
| `/#/complain` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/complain-loggedin-wcag.json) · [bp](./evidence/a11ysweep/complain-loggedin-bp.json) | issue |
| `/#/wallet` | logged in | label | heading-order, image-redundant-alt, region | [wcag](./evidence/a11ysweep/wallet-loggedin-wcag.json) · [bp](./evidence/a11ysweep/wallet-loggedin-bp.json) | issue |
| `/#/privacy-security/change-password` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/privacy-security-change-password-loggedin-wcag.json) · [bp](./evidence/a11ysweep/privacy-security-change-password-loggedin-bp.json) | issue |
| `/#/deluxe-membership` | logged in | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/deluxe-membership-loggedin-wcag.json) · [bp](./evidence/a11ysweep/deluxe-membership-loggedin-bp.json) | issue |
| remaining 29 | — | — | — | — | out of scope (see Unverified table) |

## Findings

### [High] Basket quantity −/+ and remove buttons have no accessible name
- WCAG: 4.1.2 Name, Role, Value (A) · axe `button-name`, impact critical
- Area · kind · confidence: basket · missing label · confirmed
- Symptom location: `/#/basket` (logged in, populated), 3 per item row. axe targets `.content-align.cdk-column-quantity.mat-column-quantity > .mdc-icon-button.mat-mdc-icon-button[mat-icon-button=""]:nth-child(1)`, the same path with `:nth-child(3)`, and `.cdk-column-remove.mat-column-remove > .mdc-icon-button.mat-mdc-icon-button[mat-icon-button=""]`
- Cause location: `frontend/src/app/purchase-basket/purchase-basket.component.html:31`, `:35`, `:51` · confirmed · grepped `mat-column-remove` and `(click)="delete(`. Each button holds only a Font Awesome icon (`<i class="fas fa-minus-square">`, `fa-plus-square`, `far fa-trash-alt`) and has no `aria-label`.
  ```html
  <button mat-icon-button (click)="dec(element.BasketItem.id)"><i class="fas fa-minus-square"></i></button>
  <button mat-icon-button (click)="delete(element.BasketItem.id)"><i class="far fa-trash-alt"></i></button>
  ```
- Why (verification): axe reported 3 nodes with one item in the basket. In the `agent-browser snapshot -i` accessibility tree all three appear as a bare `button` with no name ([basket-populated-snapshot.txt](./evidence/a11ysweep/basket-populated-snapshot.txt)). A screen-reader user cannot tell the decrease button from the remove button and can delete an item while trying to change its quantity.
- Fix: add an `aria-label` that includes the product name to all three (e.g. `[attr.aria-label]="'Decrease quantity of ' + element.name"`, and `'Remove ' + element.name` for the trash button). Put `aria-hidden="true"` on the icon `<i>`.

### [Medium] No control in the product list carries the product name
- WCAG: 2.5.3 Label in Name (A), 2.4.6 Headings and Labels (AA) · no axe rule in the WCAG-tag run covers this (checked by hand)
- Area · kind · confidence: product list · labels · confirmed
- Symptom location: `/#/search` (logged in and out). 15 product cards `app-product:nth-child(n) > mat-card > article > section`, 15 `button.btn-basket`
- Cause location: `frontend/src/app/product/product.component.html:22-28` (card), `:59-61` (Add to Basket) · confirmed · grepped the name from the accessibility tree, `Click for more information about the product`.
  ```html
  role="button"
  (click)="showDetail(product)"
  aria-label="Click for more information about the product"
  ```
- Why (verification): in the accessibility tree all 15 card buttons are named `Click for more information about the product` and all 15 basket buttons `Add to Basket` ([search-loggedin-snapshot.txt](./evidence/a11ysweep/search-loggedin-snapshot.txt)). The visible product name (e.g. "Apple Juice (1000ml)") is overridden by the fixed `aria-label` and is not part of the name ([label-in-name-scan.txt](./evidence/a11ysweep/label-in-name-scan.txt)). A screen-reader user tabbing through hears no product names; a speech-input user cannot say "click Apple Juice". A workaround exists: Enter on a card opens the detail dialog, which shows the product name, and Escape returns focus to the card (checked directly).
- Best-practice rules raised on the same element (no WCAG criterion): `aria-allowed-role` ×15 (impact minor, `role="button"` on `<section>`), `landmark-unique` ×1 (impact moderate).
- Fix: replace `<section role="button">` with a `<button>` and drop the fixed `aria-label`, so the product name becomes the name. Give the basket button the product name too, e.g. `[attr.aria-label]="('ADD_BASKET' | translate) + ': ' + product.name"`.

### [Medium] Toolbar search input has no label (every route)
- WCAG: 4.1.2 Name, Role, Value (A) · axe `label`, impact critical
- Area · kind · confidence: toolbar search · missing label · confirmed
- Symptom location: all 16 audited routes. axe targets `input`, `input[type="text"]`, `input[autocapitalize="none"]`, `.ng-valid` (the selector varies per route; it is the same node, `<input type="text" autocapitalize="none" placeholder="" ...>`)
- Cause location: `frontend/src/app/mat-search-bar/mat-search-bar.component.html:8-11` · confirmed · grepped `autocapitalize="none"` from the axe node. The name sits only on the outer host element, `frontend/src/app/navbar/navbar.component.html:24-25` (`<app-mat-search-bar ... aria-label="Click to search">`). The input itself has no `aria-label`, and `placeholder` defaults to `input('')` (`mat-search-bar.component.ts:33`), so it is empty.
  ```html
  <input #input type="text" [(ngModel)]="value" [placeholder]="placeholder()"
      autocapitalize="none" [tabindex]="searchVisible ? 0 : -1" />
  ```
- Why (verification): with search collapsed, axe reports 1 node per route. After pressing "Open search", the focused input has `tabindex="0"` and still no name: the accessibility tree shows `textbox` with no name, and axe re-run on the open state with `--selector '#searchQuery'` reports `label` critical ×1 ([search-open-wcag.json](./evidence/a11ysweep/search-open-wcag.json)). Screen readers announce only "edit text". The preceding "Open search" button gives some context.
- Fix: add an `aria-label` to the `<input>` in `mat-search-bar.component.html` (e.g. `[attr.aria-label]="'Search products'"` or a translation key) and remove the host element's `aria-label` (this also clears the `aria-prohibited-attr` item in the Unverified table).

### [Medium] Visible labels differ from accessible names (speech input cannot target them)
- WCAG: 2.5.3 Label in Name (A) · no default axe rule covers this (checked by hand)
- Area · kind · confidence: toolbar, login, registration, customer feedback · labels · confirmed
- Symptom and cause locations (all hard-coded `aria-label`s in templates, grepped by string, confirmed):
  | Visible text | Accessible name | Route | Cause |
  |------|------|------|------|
  | OWASP Juice Shop (logo button) | Back to homepage | all | `frontend/src/app/navbar/navbar.component.html:15` |
  | Your Basket | Show the shopping cart | all | `frontend/src/app/navbar/navbar.component.html:103-104` |
  | Log in | Login | `/#/login` | `frontend/src/app/login/login.component.html:63` |
  | Remember me | Checkbox to stay logged in or not logged in | `/#/login` | `frontend/src/app/login/login.component.html:71` |
  | Repeat Password | Field to confirm the password | `/#/register` | `frontend/src/app/register/register.component.html:50-51` |
  | Register | Button to complete the registration | `/#/register` | `frontend/src/app/register/register.component.html:117-120` |
  | Submit | Button to send the review | `/#/contact` | `frontend/src/app/contact/contact.component.html:65-67` |
- Why (verification): a script compared, for every visible control with an `aria-label`, whether the visible text (or `mat-label`) is contained in the name ([label-in-name-scan.txt](./evidence/a11ysweep/label-in-name-scan.txt)). A speech-input user who says what is on screen ("click Log in", "click Remember me") does not reach the control. The cookie banner's "Me want it!" / "But me wait!" have the same problem, but those names come from the cookieconsent library, so they are left out of the table.
- Fix: drop `aria-label` where the visible text is enough. Where extra description is needed, start the name with the visible text (e.g. "Remember me", "Your Basket").

### [Medium] Star-rating slider input in the feedback form has no name
- WCAG: 4.1.2 Name, Role, Value (A) · axe `label`, impact critical
- Area · kind · confidence: customer feedback · missing label · confirmed
- Symptom location: `/#/contact`, axe target `.mdc-slider__input` (`<input type="range" matsliderthumb ... aria-valuetext="1★">`)
- Cause location: `frontend/src/app/contact/contact.component.html:38-40` · confirmed · grepped `mat-slider`. The name is on the `<mat-slider>` host (line 39) only, not on the `<input matSliderThumb>` that takes focus (line 40). The `<label class="rating-label">` on line 38 has no `for` and is not associated with anything.
- Why (verification): axe reports `.mdc-slider__input` as a `label` violation ([contact-wcag.json](./evidence/a11ysweep/contact-wcag.json)). The submit button stays disabled without a rating (`!rating`, line 66), so the slider is required. Screen readers announce only "slider 1★".
- Fix: `<input matSliderThumb aria-label="Rating">`, or `<label id="rating-label">` plus `aria-labelledby="rating-label"`.

### [Medium] Cookie consent banner text, link and button fail contrast
- WCAG: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- Area · kind · confidence: cookie banner (first visit, every route) · contrast · confirmed
- Symptom location: `/#/search` on first visit. axe targets `#cookieconsent\:desc`, `.cc-link`, `.cc-btn`
- Cause location: `frontend/src/index.html:19-23` · confirmed · grepped `cookieconsent`. The palette is `var(--theme-text)` on `var(--theme-primary)`. `--theme-primary` comes from `frontend/src/styles.scss:100-101` (primary tone 60, computed `#438fff`); `--theme-text` from `styles.scss:350` (`#e8ecef`).
- Why (verification): axe values match the computed colors:
  | Element | Text | Background | Contrast | Required |
  |------|------|------|------|------|
  | Message (16px) | `#e8ecef` | `#438fff` | 2.67:1 | 4.5:1 |
  | "But me wait!" link (16px, after `opacity` 0.8) | `#67d033` | `#438fff` | 1.61:1 | 4.5:1 |
  | "Me want it!" button (14.4px bold) | `#e8ecef` | `#50a400` | 2.66:1 | 4.5:1 |

  Computed directly from `getComputedStyle` on the page (the link is 1.87:1 before opacity and 1.61:1 after, matching axe). Screenshot: [cookie-banner-contrast.png](./evidence/a11ysweep/cookie-banner-contrast.png). A low-vision user on a first visit has trouble reading what they are agreeing to. Once dismissed, the banner does not return.
- Fix: pin palette values in `index.html` that meet contrast (e.g. `#e8ecef` text on `--theme-background-dark` `#303030`, and `#000` text on the button instead of `#e8ecef`). Use a link color with at least 4.5:1 against the banner background.

### [Medium] Keyboard focus on Add to Basket and Checkout is barely visible
- WCAG: 2.4.7 Focus Visible (AA) · no axe rule (measured by hand)
- Area · kind · confidence: product list, basket · focus indicator · confirmed (measurement), cause inferred
- Symptom location: `button.btn-basket` on `/#/search`, the Checkout button on `/#/basket`
- Cause location: `frontend/src/app/product/product.component.scss:116-130` (no `:focus`/`:focus-visible` rule for `.btn-basket`) · inferred · grepped `focus-indicator`, `strong-focus` and `:focus` across `frontend/src/styles.scss` and the component scss; no button focus style exists (only `styles.scss:21-28`, underline on `a:focus` and `a { outline: none }`). Material's `.mat-focus-indicator::before` border computes to `rgba(0, 0, 0, 0)` (transparent), leaving only the 12% state layer.
- Why (verification): computed style after moving focus with Tab ([focus-indicator-measure.txt](./evidence/a11ysweep/focus-indicator-measure.txt)): `outline: none`, state layer `opacity 0.12` (`rgb(171,199,255)`). The button background goes from `rgb(81,107,119)` to `rgb(92,118,135)` on focus, a 1.18:1 change. In [focus-add-to-basket.png](./evidence/a11ysweep/focus-add-to-basket.png) the first Add to Basket has focus and is hard to tell apart from its neighbors. For comparison, the toolbar text buttons use the same 0.12 layer but a pill shape appears where there was no background before, so the focus shows ([focus-navbar-account.png](./evidence/a11ysweep/focus-navbar-account.png)); they are not included here. Product cards (`section`) show the browser default `outline: auto`.
- Fix: add `@include mat.strong-focus-indicators((border-color: #e8ecef));` to the global styles, or `.btn-basket:focus-visible, .mat-mdc-raised-button:focus-visible { outline: 3px solid #e8ecef; outline-offset: 2px; }`.

### [Medium] About page customer-feedback carousel cannot be operated by keyboard
- WCAG: 2.1.1 Keyboard (A) · axe `scrollable-region-focusable`, impact serious
- Area · kind · confidence: About · keyboard · confirmed (0 focusable elements); autoplay unverified
- Symptom location: `/#/about`, axe target `.g-slider`
- Cause location: `frontend/src/app/about/about.component.html:42-54` (`<gallery id="feedback-gallery" [autoplay]="true" ...>`) · inferred · grepped `feedback-gallery`. The prev/next arrows (`i.g-nav-next`) are rendered by the ng-gallery library with `tabIndex -1`. The library source (node_modules) is not in the copy, so it was not opened.
- Why (verification): the gallery contains 0 elements with `tabIndex >= 0`. Over 15 seconds the active slide stayed at index 0 (autoplay may be paused in a headless session, so 2.2.2 is not judged). A keyboard user sees only the first feedback entry; no keyboard workaround to reach the rest was found. Medium under report-base rule 9 (degraded).
- Fix: enable ng-gallery's keyboard navigation, or render the feedback as a plain text list below the gallery. If autoplay stays, add a pause control.

### [Medium] About body link is distinguished by color only, 1.31:1 against surrounding text
- WCAG: 1.4.1 Use of Color (A) · axe `link-in-text-block`, impact serious
- Area · kind · confidence: About · color reliance · confirmed
- Symptom location: `/#/about`, axe target `a[href$="legal.md"]`
- Cause location: `frontend/src/styles.scss:14-18` (`a:link, a:visited { color: tertiary; text-decoration: none; }`); the link itself is `frontend/src/app/about/about.component.html:29` · confirmed · grepped `legal.md` from the axe target.
- Why (verification): link `#70e000`, surrounding paragraph `#e3e2e6` (computed), 1.31:1 and no underline. The underline appears only on hover/focus (`styles.scss:21-24`). Users who cannot tell the colors apart have trouble finding the link in the paragraph. Workaround: the link is reachable with Tab and gets an underline on focus. A barrier with a workaround is Medium under rule 9.
- Fix: always underline links inside paragraphs (`p a { text-decoration: underline }`).

### [Low] User email in the basket heading has 1.65:1 contrast
- WCAG: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- Area · kind · confidence: basket · contrast · confirmed
- Symptom location: `/#/basket` (logged in, empty and populated), axe target `small`
- Cause location: `frontend/src/app/purchase-basket/purchase-basket.component.scss:19-20` · confirmed · traced from `<small>{{userEmail}}</small>` in `purchase-basket.component.html:9` to the `h1 small` rule.
  ```scss
  h1 small {
    color: rgba(0, 0, 0, 0.6);
  ```
- Why (verification): 60% black on the dark card background `rgb(62,62,62)`. Blended text color `#191919`, computed contrast 1.65:1 (axe 1.64:1), 25.6px bold (large text, 3:1 required). Screenshot: [basket-heading-contrast.png](./evidence/a11ysweep/basket-heading-contrast.png). Looks like a light-theme value left in the dark theme. Low because the hidden information is the logged-in user's own email.
- Fix: use a theme variable such as `color: var(--theme-text-darker)` (`#b8c0c7`).

### [Low] Low-stock ribbon ("Only 1 left") fails contrast
- WCAG: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- Area · kind · confidence: product list · contrast · confirmed
- Symptom location: `/#/search`, axe target `app-product:nth-child(6) > mat-card > article > aside > span[translate=""]`
- Cause location: `frontend/src/app/product/product.component.scss:91-100` (`.ribbon { background-color: var(--theme-accent); font: 700 18px/1 ...; text-shadow: 0 1px 1px rgba(0,0,0,0.2) }`), template `product.component.html:10-15` · confirmed · grepped `ribbon`.
- Why (verification): text `#e3e2e6` on ribbon background `#50a400`, 18px bold (13.5pt, under the 14pt-bold large-text threshold, so 4.5:1 applies). Computed contrast 2.45:1; axe reports 2.86:1 against the text-shadow color `#4a9700`. Low-vision users can miss the stock warning.
- Fix: use `#000` ribbon text or a darker green background (`--theme-accent-dark`), and confirm at least 4.5:1.

### [Low] About carousel images have no alt
- WCAG: 1.1.1 Non-text Content (A) · axe `image-alt`, impact critical
- Area · kind · confidence: About · text alternative · confirmed
- Symptom location: `/#/about`, axe targets `.g-active-item > gallery-image[imagestate="success"] > .g-image-item[loading="lazy"]` and `gallery-item[galleryindex="1"] > ...` (axe reported the 2 loaded images; all 8 `.g-image-item` on the page lack `alt`)
- Cause location: `frontend/src/app/about/about.component.ts:124-127` · confirmed · grepped `galleryRef.addImage`. Only `{ src, args }` is passed, no `alt`.
- Why (verification): the images are background photos behind the feedback caption (`figcaption`). Screen readers may announce an unnamed image or its file name. The caption text is read separately, so little information is lost.
- Fix: pass `alt: ''` so the background photos are treated as decorative.

### [Low] Basket table header row has no cells
- WCAG: 1.3.1 Info and Relationships (A) · axe `aria-required-children`, impact critical
- Area · kind · confidence: basket · table structure · confirmed
- Symptom location: `/#/basket` (empty and populated), axe target `mat-header-row`
- Cause location: `frontend/src/app/purchase-basket/purchase-basket.component.html:57` (`<mat-header-row>`) with each column's `<mat-header-cell ... class="header-hidden">` (lines 13, 22, 28, 42, 49), and `purchase-basket.component.scss:127-128` (`.header-hidden { display: none; }`) · confirmed · grepped `header-hidden`.
- Why (verification): every header cell is empty and `display: none`, so the `role="row"` has no child cells. Screen-reader table navigation gives no column names (product, quantity, price).
- Fix: put column names in the header cells and hide them visually only (`cdk-visually-hidden`) instead of `display: none`.

### [Low] Page content sits outside landmarks (no `<main>`)
- Classification: axe best practice `region`, impact moderate · no WCAG criterion
- Area · kind · confidence: app shell · landmarks · confirmed
- Symptom location: all 16 audited routes. Representative targets `.search-area`, `h1`, form field labels (10 on `/#/login`, 14 on `/#/register`, 22 on `/#/photo-wall`, etc.)
- Cause location: `frontend/src/app/app.component.html:15` (`<router-outlet>` directly inside `mat-sidenav-container`, no `<main>`), search box `frontend/src/app/navbar/navbar.component.html:22` (`<div class="search-area">`) · confirmed · grepped the axe target `.search-area` and read the app shell template.
- Why (verification): the best-practice run reports `region` on every route. Screen-reader landmark navigation cannot jump to the main content.
- Fix: wrap `<router-outlet>` in `app.component.html` with `<main>`, and check that the toolbar sits inside a `<nav>`/`header` landmark.

### [Low] Image alt text repeats adjacent text
- Classification: axe best practice `image-redundant-alt`, impact minor · no WCAG criterion
- Area · kind · confidence: toolbar logo, product cards, basket · text alternative · confirmed
- Symptom location: `.logo`/`img` (logo) on every route; 15 product images on `/#/search` such as `img[alt="Apple Juice (1000ml)"]`
- Cause location: `frontend/src/app/navbar/navbar.component.html:17-18` (`alt={{applicationName}}` followed by the same `{{applicationName}}` text), `frontend/src/app/product/product.component.html:41`, `:46` (`alt="{{ product.name }}"` followed by `{{ product.name }}`) · confirmed · grepped `.logo` and `alt=` from the axe targets.
- Why (verification): screen readers read the same text twice.
- Fix: `alt=""` for images that sit next to the same text.

### [Low] First-visit welcome dialog has no accessible name
- Classification: axe best practice `aria-dialog-name`, impact serious · no WCAG criterion
- Area · kind · confidence: first-visit welcome dialog · labels · confirmed
- Symptom location: `/#/search` first visit, axe target `#mat-mdc-dialog-0`
- Cause location: `frontend/src/app/welcome/welcome.component.ts:35-41` · confirmed · grepped `dialog.open(WelcomeBannerComponent`. Options are only `minWidth`, `width`, `position`; no `ariaLabelledBy`/`ariaLabel`.
- Why (verification): when the dialog opens, screen readers do not announce its title ("Welcome to OWASP Juice Shop!").
- Fix: set `ariaLabelledBy` to the id of the banner's `h1`.

### [Low] Wallet page heading level jumps from h1 to h3
- Classification: axe best practice `heading-order`, impact moderate · no WCAG criterion
- Area · kind · confidence: wallet · heading structure · confirmed
- Symptom location: `/#/wallet`, axe target `.mdc-card[_ngcontent-ng-c4216643156=""] > h3`
- Cause location: `frontend/src/app/wallet/wallet.component.html:10` (`<h1>`), `:14` (`<h3>`) · confirmed · grepped `<h3`.
- Why (verification): screen-reader users navigating by headings get a structure with no h2.
- Fix: make line 14 an `<h2>`.

## Keyboard walk (beyond the findings)
- `/#/login` ([login-tab-order.txt](./evidence/a11ysweep/login-tab-order.txt)): 6 toolbar controls → email → password → show password → "Forgot your password?" → Remember me → "Not yet a customer?" → end of document → back to the toolbar. Order matches the visual order; no trap. The login button is `disabled` while the fields are empty and so is not in the order (it enables once values are entered). Links get an underline on focus. The collapsed search input (`tabindex="-1"`) is skipped.
- `/#/search` ([search-tab-order.txt](./evidence/a11ysweep/search-tab-order.txt)): card → Add to Basket for each product. Enter on a card opens the detail dialog with focus inside it; Escape returns focus to the card. Enter on Add to Basket adds the item (this check added Apple Pomace to the run's own basket).

## Unverified
| Item | Reason | How to check manually |
|------|------|------|
| `aria-prohibited-attr`: `#searchQuery` (every route), `#rating` and `#captcha` (`/#/contact`) | axe `incomplete`: cannot decide whether `aria-label` is supported on role-less elements (`app-mat-search-bar`, `mat-slider`, `code`) | Check with NVDA/VoiceOver whether the name is announced on those elements |
| Form input contrast: `/#/login` `#email` `#password`, `/#/register` `#emailControl` `#passwordControl` and hints, `/#/forgot-password`, `/#/contact` `#comment` `#captchaControl`, `/#/complain` `#complaintMessage`, `/#/wallet`, 7 on `/#/address/create`, 3 on `/#/privacy-security/change-password` | axe `incomplete`: the floating label overlaps, so the background cannot be determined | Measure text vs field background with values entered |
| Add to Basket label contrast (`/#/search`) | axe `incomplete` (pseudo-element background). Hand calculation gives white on `rgb(81,107,119)` = 5.65:1, but that is not an axe verdict, so it is not counted as a pass | Re-check the figure with another tool |
| 3 text nodes on the `/#/deluxe-membership` card | axe `incomplete`: background gradient | Measure against the lightest point of the gradient |
| `/#/photo-wall` photo caption contrast | axe `incomplete`: pseudo-element background | Measure with the overlay shown |
| `/#/basket` quantity "1" contrast | axe `incomplete`: text too short | Measure by hand |
| `bypass` (`/#/order-history`, `/#/deluxe-membership`) | axe `incomplete`: found no skip link, heading or landmark but withheld a verdict | Re-run with orders present; check for a skip link |
| `aria-hidden-focus` (welcome dialog open) | axe `incomplete`: `app-root` is `aria-hidden="true"` while focus-trap anchors exist | With the dialog open, Tab and see whether focus leaves it |
| About carousel autoplay (2.2.2) | slide did not change in 15 seconds in the headless session, so no verdict | Check autoplay and a pause control in a normal browser |
| Actual screen-reader output | no screen reader was run; name-related judgments come from Chrome's accessibility tree | Check the product list and basket with NVDA/VoiceOver |
| Keyboard walk on routes other than login and the product list | only those two screens were walked | `agent-browser press Tab` and record the focused element |
| Locale parity, mobile viewport and tap targets | not in the approved plan | Switch locale via the language menu and re-audit; `set viewport 390 844` |
| 29 out-of-scope routes: `administration`, `accounting`, `address/select`, `address/edit/:addressId`, `delivery-method`, `order-completion/:id`, `order-summary`, `payment/:entity`, `recycle`, `hacking-instructor`, `score-board`, `track-result`, `track-result/new`, `2fa/enter`, `privacy-security` and its children `privacy-policy`, `two-factor-authentication`, `data-export`, `last-login-ip`, `juicy-nft`, `wallet-web3`, `web3-sandbox`, `chatbot` and its 2 children, `bee-haven`, `coding-challenge/:challengeKey`, `403`, `**` | not selected for this run. Routes where a visit can register as a solved challenge (`score-board`, `privacy-policy`) were excluded per the plan (no deliberate challenge solving). Routes that need an admin account or an order in progress were also excluded | Run the same two axe passes per route |

## Screenshot and evidence index
- `evidence/a11ysweep/<route>[-loggedin]-wcag.json`, `-bp.json`: raw axe results per route (axe 4.12.1). No tokens or cookies.
- `evidence/a11ysweep/search-open-wcag.json`: axe scoped to `#searchQuery` with search open
- `evidence/a11ysweep/home-welcome.png`: first visit, welcome dialog and cookie banner
- `evidence/a11ysweep/cookie-banner-contrast.png`: cookie banner (welcome dialog dismissed)
- `evidence/a11ysweep/basket-heading-contrast.png`: basket heading email contrast, quantity/remove icon buttons
- `evidence/a11ysweep/focus-add-to-basket.png`: keyboard focus on the first Add to Basket button
- `evidence/a11ysweep/focus-navbar-account.png`: keyboard focus on the toolbar Account button (comparison)
- `evidence/a11ysweep/search-loggedin-snapshot.txt`, `basket-populated-snapshot.txt`: `agent-browser snapshot -i` accessibility tree
- `evidence/a11ysweep/label-in-name-scan.txt`: visible text vs accessible name
- `evidence/a11ysweep/focus-indicator-measure.txt`: computed focus indicator values per Tab stop
- `evidence/a11ysweep/login-tab-order.txt`, `search-tab-order.txt`: Tab order records
