# a11ysweep report — OWASP Juice Shop (2026-09-08)

> English version. The default-language (Korean) report is [`a11ysweep-report.md`](./a11ysweep-report.md). Same run, same findings.

## Environment
- Target: OWASP Juice Shop 20.2.0 (docker `bkimminich/juice-shop`, source `1618a61`)
- Run: `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop` · `http://localhost:3000`
- Driver: axe-core 4.10.2 injected via CDN into the live page with agent-browser 0.37.0 (`evaluate`), running `axe.run(document,{resultTypes:['violations']})`. Juice Shop has no CSP, so the injection succeeded outright.
- Audited routes: `/#/search`, `/#/login`, `/#/register`

## Summary
- By axe impact: Critical 1 rule · Moderate 3 rules · Minor 2 rules
- Coverage: 3/41 routes (representative) · many unverified (below)
- Every number is a count of axe-core rule-violation nodes, with the evidence stated per rule.

## Route coverage
| Route | axe violation rules | Representative violations |
|------|------|------|
| `/#/search` | 6 | aria-allowed-role ×15, image-redundant-alt ×16, label ×1, landmark-* ×3, region ×3 |
| `/#/login` | 3 | label ×1, region ×13, image-redundant-alt ×1 |
| `/#/register` | 3 | label ×1, region ×16, image-redundant-alt ×1 |

## Findings

### [CRITICAL] Form input has no accessible label (axe `label`)
- WCAG: 4.1.2 Name, Role, Value / 1.3.1 · confidence: confirmed
- Location: all three routes. Node target `input[type="text"]` — the collapsed search input in the top toolbar (`tabindex="-1"`, `placeholder=""`, no label)
- Why (verification): `axe.run(document,{runOnly:['label']})` returned 1 violation on each route. The returned node HTML is a text input with empty label, `aria-label`, and placeholder. A screen-reader user cannot tell what the input is for.
- Suggested fix: give the search input `aria-label="Search products"`. When collapsed, remove it from the DOM or exclude it from the focus order entirely (it is `tabindex="-1"` today, but axe's accessibility tree still sees an unnamed control).

### [MODERATE] Page content sits outside landmarks (axe `region`)
- Classification: axe best practice, no WCAG criterion · confidence: confirmed
- Location: `/#/login` ×13, `/#/register` ×16, `/#/search` ×3. Representative targets `.search-area`, notification cards (`.accent-notification .mdc-card .notificationMessage`)
- Why (verification): `axe.run(...runOnly:['region'])` flagged content blocks that are not contained by a landmark such as `main`/`nav`. Screen-reader landmark navigation cannot skip to them, forcing linear traversal.
- Suggested fix: wrap the main content in `<main>` and give the notification area an appropriate role.

### [MODERATE] Nested / duplicate landmarks (axe `landmark-complementary-is-top-level`, `landmark-unique`)
- Classification: axe best practice, no WCAG criterion · confidence: confirmed
- Location: `/#/search` — `landmark-complementary-is-top-level` ×2, `landmark-unique` ×1
- Why (verification): axe reported that an `aside` (complementary) is nested inside another landmark, and that same-role landmarks are duplicated without an accessible name.
- Suggested fix: raise the complementary landmark to the top level, and give duplicate landmarks unique `aria-label`s.

### [MINOR] Image alt text duplicates adjacent text (axe `image-redundant-alt`)
- Classification: axe best practice, no WCAG criterion · confidence: confirmed
- Location: `/#/search` ×16 (product card images), `/#/login` ×1, `/#/register` ×1
- Why (verification): axe flagged image `alt` repeating the neighboring text (product name, etc.). A screen reader reads the same phrase twice.
- Suggested fix: empty the `alt` (`alt=""`) on decorative/duplicate images, or keep only information the text does not carry.

### [MINOR] Element has an ARIA role not allowed for it (axe `aria-allowed-role`)
- Classification: axe best practice, no WCAG criterion · confidence: confirmed
- Location: `/#/search` ×15
- Why (verification): axe reported a role assigned to an element type that does not allow it.
- Suggested fix: adjust the flagged elements' roles to match their semantics, or remove them.

## Unverified
| Item | Reason | How to check manually |
|------|------|------|
| Keyboard focus order / focus-ring visibility | this run used static axe rules; no Tab traversal | repeat `agent-browser press Tab` + `snapshot` to track the focused element, screenshot the focus ring |
| Post-login screens (basket/order etc.) a11y | axe ran only the 3 logged-out routes | inject and run the same in a jim login session |
| Color contrast (numeric) | this run used axe's default ruleset; `color-contrast` not tallied separately | run `axe.run(...runOnly:['color-contrast'])` |
| The other 38 routes | only 3 representative routes audited | repeat per route |

## Note
The axe-core CLI (`@axe-core/cli`) needs a separate chromedriver and failed to run in this environment. Instead the library was injected into the already-rendered page (using the driver's capability); the fact that injection was possible at all is itself consistent with breachsweep's finding that there is no CSP.
