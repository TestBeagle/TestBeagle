# emit-runner — generate a static, repo-native `.sh` runner

Shared by scriptify and by each dimension skill's optional "emit a runner" step. Goal: freeze a flow the agent already figured out into a script the maintainer can re-run with no agent.

## Rules

1. **Reuse the repo's own style first.** If the repo already has capture/run scripts (found in preflight), match their shape, flags, and location — don't introduce a second convention. Extend, don't replace.
2. **Only script what you actually ran and verified.** A runner is a recording of a working flow, not a guess. Don't emit steps you couldn't execute. Flows driven with agent-browser port straight into a runner (they are shell commands), but replace per-snapshot `@eN` refs with stable semantic locators (`agent-browser find role|text|label|testid …`) and bounded readiness (`wait --load networkidle`, `wait <sel>`) — a raw `@eN` ref is only valid for the snapshot that produced it and will break on replay. Open a named session at the top (`export AGENT_BROWSER_SESSION="runner-$(date +%s)-$$"`, unique per run), add a cleanup trap and `agent-browser close` at the end, and verify the script twice from a fresh seeded state. MCP-driven flows can't be frozen — re-drive them with agent-browser first or leave them out.
3. **Portable bash** when there's no existing template:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   # env-parameterized, no hardcoded absolute paths or bundle ids
   : "${API_BASE_URL:=http://localhost:4000}"
   OUT="${OUT:-docs/qa/screenshots/$(date +%F)}"
   mkdir -p "$OUT"
   # ... the discovered launch/seed/capture commands ...
   echo "wrote: $OUT"
   ```
   Idempotent (safe to re-run), reads the bundle id / package from build output rather than hardcoding, and echoes every artifact path it wrote.
4. **Carry the hard rules into the generated script** (they must survive without the agent):
   - Android: `am start -n …`, never `monkey`; `adb uninstall` only within the approved data-reset scope; keep `install -r` for upgrade/data-retention flows.
   - iOS: after building, grep the log for `BUILD SUCCEEDED` and exit non-zero on `BUILD FAILED` (build wrappers can exit 0 on failure).
5. **Write location**: the repo's existing `scripts/` (or wherever its current scripts live); else what `../beagle-shared/capture-output.md` resolves. `chmod +x` it.
6. **Verify before handing over**: run the emitted script twice from a fresh seeded state and confirm it produces the expected artifacts. A runner that wasn't run is unverified — say so and don't claim it works.
7. **Offer, don't auto-commit.** Present the script + a one-line usage note; let the maintainer commit it.
