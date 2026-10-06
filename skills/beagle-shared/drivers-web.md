# beagle-web-driver — web capture & interaction recipes

Shared by bugsweep, breachsweep, a11ysweep, perfsweep, snap, repro, scriptify. Pick the richest driver the runtime actually has, in this order, and state in the plan which one you're using and what it can't do. Put the driver name and version on the report's 드라이버 line.

| Order | Driver | Interaction | Console / network | Video | Works in |
|---|---|---|---|---|---|
| 1 | Repo's own E2E runner (Playwright / Cypress / WebdriverIO) | yes, for flows it already covers | yes | per tool | anywhere |
| 2 | **agent-browser** CLI (`command -v agent-browser`) | yes | yes | yes (`record`, needs ffmpeg) | Claude Code, Codex, any shell |
| 3 | Browser MCP (`chrome-devtools` or `claude-in-chrome`) when connected | yes | yes | GIF only (claude-in-chrome) | runtimes that load MCP |
| 4 | Headless Chrome CLI | **no** | **no** | no | anywhere with Chrome |

Driver 1 beats 2 only for flows the repo already scripts; use 2 for everything else. Driver 3 is worth using alongside 2 for what it uniquely has (chrome-devtools `lighthouse_audit` and trace insights). Driver 4 is capture-only: every flow, console check, and network check it can't do goes in the report's 검증 불가 table, never counted as pass.

## Driver 2 — agent-browser (preferred interactive driver)

Verified against agent-browser 0.37.0. Full guide ships with the CLI: `agent-browser skills get core` (read it once per session; it is version-matched, this file only pins what TestBeagle relies on). Not installed? Preflight reports it with the fix: `brew install agent-browser` or `npm i -g agent-browser && agent-browser install` (the latter downloads Chrome for Testing — an install, so it needs approval).

```bash
# one unique session per run — the unnamed default is shared with every other agent on the machine
export AGENT_BROWSER_SESSION="beagle-$(date +%s)-$$"

agent-browser open "http://localhost:PORT/route"
agent-browser wait --load networkidle              # readiness by evidence, not sleep
agent-browser snapshot -i                          # interactive elements with refs: link "Install" [ref=e26]
agent-browser click @e26                           # refs go stale after any page change → re-snapshot
agent-browser fill @e3 "user@example.com"          # clear + type; `type` appends; `press Enter`
agent-browser find text "Log in" click             # semantic locator when a ref isn't handy (role/text/label/placeholder/testid)
agent-browser get url; agent-browser get title     # assert where you landed
agent-browser eval "document.querySelectorAll('.item').length"

# after EVERY route — capture these as evidence, then judge against what's expected
agent-browser console                              # console.* output
agent-browser errors                               # uncaught page errors
agent-browser network requests                     # non-2xx/3xx, failed, slow

# capture
agent-browser screenshot OUT/route-state.png       # viewport
agent-browser screenshot --full OUT/route-state-full.png
agent-browser set media dark                       # then capture the dark variant (`set media light` to restore)
agent-browser set viewport 390 844                 # mobile viewport variant

# video (repro): real .webm/.mp4, needs ffmpeg with libvpx/libx264 on PATH
agent-browser record start OUT/repro.webm && ...steps... && agent-browser record stop

# perf (perfsweep): Chrome DevTools trace around an interaction
agent-browser trace start && ...interact... && agent-browser trace stop OUT/trace.json

agent-browser close                                # always, when the run ends
```

Console, page-error, and network output are **evidence candidates, not automatic findings**. Report only what deviates from the expected result for that step — a negative test's 401, an intentional validation error, or a known third-party beacon is expected, not a bug. Correlate each signal to the action that triggered it and, if the source is available, to the code that emitted it, and deduplicate repeats across routes into one finding.

Because every step is a shell command, a flow verified with agent-browser can be **frozen into a static runner** (`../beagle-shared/emit-runner.md`) — but rewrite any `@eN` snapshot refs as stable semantic locators (`find role|text|label|testid`) first, since a ref is only valid for the snapshot that produced it. An MCP-driven flow can't be frozen this way.

## Driver 3 — browser MCP

Use when connected. Before relying on any driver or CLI, confirm it actually exists and note its version (an exposed MCP tool, `agent-browser --version`, `google-chrome`/`chromium`, `chromedriver`, `ffmpeg`, the audit packages) — declare anything missing in the plan rather than discovering it mid-run. Tool names below are the actual ones.

- **chrome-devtools**: `new_page` / `navigate_page`, `take_screenshot`, `take_snapshot`, `click`, `fill`, `fill_form`, `hover`, `press_key`, `type_text`, `drag`, `wait_for`, `evaluate_script`, `list_console_messages`, `list_network_requests`, `emulate` (color scheme, device, throttling), `resize_page`, `performance_start_trace` → interact → `performance_stop_trace` → `performance_analyze_insight`, `lighthouse_audit`.
- **claude-in-chrome**: `tabs_create_mcp` + `navigate`, `computer` (screenshot/click/type/scroll), `read_page`, `find`, `form_input`, `read_console_messages`, `read_network_requests`, `resize_window`, `javascript_tool`, `gif_creator` (GIF, not video). Note: this extension talks to a visible Chrome and may refuse `localhost` targets — if it does, fall back to agent-browser rather than losing interaction.

One tab per top-level route; check console and network after every route, same as Driver 2.

## Driver 4 — headless Chrome CLI (capture-only fallback)

```bash
CHROME="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
[ -z "$CHROME" ] && [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -z "$CHROME" ] && echo "no Chrome found" && exit 1
mkdir -p OUT
rm -f OUT/route-name.png   # fresh path, so a stale file from a prior run can't pass as this capture
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 \
  --window-size=1280,800 --screenshot="OUT/route-name.png" "http://localhost:PORT/route"
test -s OUT/route-name.png || { echo "FAIL: screenshot missing/empty for route-name" >&2; exit 1; }   # fail hard; a bad capture is otherwise silent
"$CHROME" --headless=new --dump-dom "http://localhost:PORT/route" > OUT/route-name.html   # HTML for scraping/secret checks
```

Dark mode: `--force-dark-mode` (best-effort; say so in the report if the app doesn't honor it). Mobile viewport: `--window-size=390,844`. No interaction, no console, no network: report those as 검증 불가.

## Accessibility and performance CLIs (any driver)

- axe violations + contrast: `agent-browser a11y --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa --json` on the live page (bundled axe-core, works logged in). Fallback: `npx @axe-core/cli http://localhost:PORT/route` (needs Chrome **and a matching chromedriver**, logged-out only). Keyboard/focus order needs an interactive driver: `agent-browser press Tab` repeatedly, `snapshot` to read the focused element, screenshot the focus ring.
- Core Web Vitals on a live/logged-in page: `agent-browser vitals --json`.
- Lighthouse (≥3 runs, report the median): `npx lighthouse http://localhost:PORT/route --only-categories=performance --output=json --quiet --chrome-flags="--headless=new"`.
- **`@axe-core/cli` and the Lighthouse CLI load the URL in a fresh, logged-out browser — they do not carry your session** (`agent-browser a11y`/`vitals` run on the current page and do). For an authenticated screen, inject axe into the already-authenticated page (agent-browser/MCP) or transfer the session, and **verify the account and final URL before auditing** so a login redirect isn't audited as the target. Keep credentials, tokens, and session/state files out of the captured artifacts.

## Output

Write captures to the location `../beagle-shared/capture-output.md` resolves for this repo. Name files per `../beagle-shared/capture-output.md` (e.g. `settings-loggedin-dark.png`).
