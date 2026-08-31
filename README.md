# shakeout

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

**Give your app the shakeout: an agent-driven, plan-gated test suite that runs a project locally, walks every user path, and writes an evidence-based report — the same way in Claude Code and Codex CLI.**

shakeout is a set of portable agent **skills**. Point any of them at a repo you can run locally (web, iOS, Android, API, or a monorepo) and the agent discovers how it runs, gets your approval on a route map, then launches it, captures every screen, exercises the flows, and reports what it found — with an explicit list of what it could *not* verify. It never invents a pass.

## Skills

| Skill | What it does | Say something like |
|-------|--------------|--------------------|
| **preflight** | Foundation. Checks whether the repo can be run/tested locally: project type, toolchain, how it runs, where screenshots/media go. Run this first. | "preflight this repo", "테스트 가능한 환경인지 봐줘" |
| **bugsweep** | Full-path functional QA: screenshots/video of every screen + real interaction across all flows (signup → every feature). | "전수 QA 해줘", "screenshot every screen" |
| **breachsweep** | Security testing of an app **you own**: authz/IDOR, injection, secret exposure, headers, cookies/CORS. Local, non-destructive. | "보안 점검", "pentest my app" |
| **a11ysweep** | Accessibility & UX: contrast, tap-target size, ARIA/labels, keyboard nav, locale parity, AI UI slop. | "접근성 점검", "a11y audit" |
| **perfsweep** | Performance: Lighthouse, load time, jank, bundle size, low-power/energy use. | "성능 점검", "Lighthouse" |
| **scriptify** | Turns a discovered flow into a committed, repo-native static `.sh` runner so it re-runs **without an agent**. | "정적 스크립트로 만들어줘", "make a capture script" |

Every run is **plan-gated**: the agent shows you the route map and waits for approval before it launches, seeds, or captures anything. In Claude Code this uses plan mode; in Codex it posts the plan and waits for your explicit OK. Reports default to Korean and land in the repo (e.g. `docs/qa/`), reusing the project's own conventions where they exist.

## Requirements

- `git` and `bash` (all skills).
- **Web** targets: Google Chrome. Interaction/console/network capture is best with the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp); without it, skills fall back to capture-only headless Chrome.
- **iOS** targets: Xcode + `xcrun simctl` (macOS).
- **Android** targets: Android SDK platform-tools (`adb`).

> Codex CLI: to give the web driver full interaction, enable the chrome-devtools MCP in `~/.codex/config.toml` (`[mcp_servers.chrome-devtools] command="npx" args=["chrome-devtools-mcp@latest"]`). Otherwise web QA degrades to capture-only and reports the gap honestly.

## Install

Clone anywhere, then symlink the skills into whichever agent runtime(s) you use. Re-running is safe.

```bash
# 1) Clone
git clone https://github.com/ted-plab/shakeout.git
cd shakeout
SHAKEOUT_DIR="$(pwd)"

# 2) Symlink into your runtime(s)
SKILLS="preflight bugsweep breachsweep a11ysweep perfsweep scriptify"
SHARED="drivers-web.md drivers-mobile.md capture-output.md report-base.md emit-runner.md"
for dir in ~/.claude/skills ~/.codex/skills ~/.agents/skills; do
  mkdir -p "$dir"
  for s in $SKILLS; do ln -sfn "$SHAKEOUT_DIR/$s"  "$dir/$s"; done
  for f in $SHARED; do ln -sfn "$SHAKEOUT_DIR/$f"  "$dir/$f"; done
done
```

- `~/.claude/skills` — Claude Code
- `~/.codex/skills` — Codex CLI (`$CODEX_HOME/skills`)
- `~/.agents/skills` — cross-runtime alias read by Codex, Copilot CLI, and Gemini CLI

The `SHARED` files are symlinked next to the skill folders so each skill's `../<shared>.md` reference resolves under a symlinked install. They carry no `SKILL.md`, so runtimes don't treat them as skills.

## Usage

Open your agent in the repo you want to test and ask, in plain language:

- `preflight this repo` — is it runnable/testable locally, and how?
- `run a full QA pass on the web app` — bugsweep walks every route and reports.
- `security-check my API` — breachsweep, after you confirm scope and authorization.
- `make a static capture script` — scriptify emits a `.sh` you can re-run yourself.

Each skill presents its plan and waits for your approval before doing anything to the app.

## Safety

**breachsweep** tests only apps **you own or are authorized to test**, against a **local** instance, and is **non-destructive** by default (no data deletion, no DoS, no mass requests, never production or third-party services). Reports include the minimum reproduction needed to fix an issue — not a weaponized exploit.

## License

Apache License 2.0 — see [LICENSE](./LICENSE). Copyright © 2026 Ted Lee.
