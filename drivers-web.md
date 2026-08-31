# drivers-web — web capture & interaction recipes

Shared by bugsweep, breachsweep, a11ysweep, perfsweep, scriptify. Pick the richest driver the runtime actually has; state in the plan which one you're using and what it can't do.

## Driver A — browser MCP (preferred: full interaction)

Use a browser-automation MCP if one is connected (`chrome-devtools` or `claude-in-chrome`). It gives real navigation, interaction, and console/network inspection. Capabilities to use, by the tool that provides them (names vary slightly by server — use whichever is present):

- **Open / navigate**: `new_page` / `navigate_page` (chrome-devtools), or `tabs_create_mcp` + `navigate` (claude-in-chrome). One tab per top-level route.
- **Screenshot**: `take_screenshot`. Full-page where supported; otherwise scroll and stitch or capture the key viewport.
- **Read structure** (for assertions / a11y tree): `take_snapshot` (accessibility snapshot) or `read_page`.
- **Interact**: `click`, `fill`, `fill_form`, `hover`, `press_key`, `type_text`, `drag`. Drive real flows: signup, login, navigation, CRUD.
- **Console errors** — check after every route: `list_console_messages` (filter to error/warning). A route with console errors is a finding.
- **Network errors** — check after every route: `list_network_requests` (flag non-2xx/3xx, failed, and slow requests).
- **Dark mode / viewport / locale**: `emulate` (color-scheme, device, network throttle) and `resize_page`. Capture each approved variant.
- **Performance** (perfsweep): `performance_start_trace` → interact → `performance_stop_trace`, then read insights. Lighthouse via `lighthouse_audit` if available.
- **Accessibility** (a11ysweep): inject axe-core with `evaluate_script`:
  ```js
  // load axe from the app's own bundle if present, else from a CDN the page allows
  await axe.run(document, { resultTypes: ['violations'] })
  ```
  Also walk keyboard focus order with repeated `press_key` "Tab" and record the visible focus ring.

Wait for readiness between steps with `wait_for` (text/selector) rather than fixed sleeps.

## Driver B — headless Chrome CLI (fallback: capture-only)

When no browser MCP is connected (common in Codex). Deterministic screenshots, but **no interaction, no per-route console/network** — put every flow, console check, and network check in the report's "검증 불가 / unverified" section, unless the repo ships its own E2E tool (Playwright, Cypress, WebdriverIO) — reuse that instead of this fallback.

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS; else `google-chrome`/`chromium`
mkdir -p OUT
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1280,800 --screenshot="OUT/route-name.png" "http://localhost:PORT/route"
test -s OUT/route-name.png || echo "WARN: screenshot missing/empty for route-name"   # a failed capture is otherwise silent
# HTML for scraping/secret checks:
"$CHROME" --headless=new --dump-dom "http://localhost:PORT/route" > OUT/route-name.html
```

Dark mode: add `--force-dark-mode` (best-effort; note it in the report if the app doesn't honor it). Mobile viewport: `--window-size=390,844`.

If the repo already has an E2E runner, prefer it for flows:

```bash
npx playwright test           # or the repo's own test script
npx playwright screenshot URL out.png   # ad-hoc capture
```

## Output

Write captures to the location `capture-output.md` resolves for this repo. Name files by `route[-state][-variant]` (e.g. `settings-loggedin-dark.png`) so the report index is scannable.
