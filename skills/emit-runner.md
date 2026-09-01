# emit-runner — generate a static, repo-native `.sh` runner

Shared by scriptify and by each dimension skill's optional "emit a runner" step. Goal: freeze a flow the agent already figured out into a script the maintainer can re-run with no agent.

## Rules

1. **Reuse the repo's own style first.** If the repo already has capture/run scripts (found in preflight), match their shape, flags, and location — don't introduce a second convention. Extend, don't replace.
2. **Only script what you actually ran and verified.** A runner is a recording of a working flow, not a guess. Don't emit steps you couldn't execute.
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
   - Android: `am start -n …`, never `monkey`; `adb uninstall` before `adb install`.
   - iOS: after building, grep the log for `BUILD SUCCEEDED` and exit non-zero on `BUILD FAILED` (build wrappers can exit 0 on failure).
5. **Write location**: the repo's existing `scripts/` (or wherever its current scripts live); else what `capture-output.md` resolves. `chmod +x` it.
6. **Verify before handing over**: run the emitted script once and confirm it produces the expected artifacts. A runner that wasn't run is unverified — say so and don't claim it works.
7. **Offer, don't auto-commit.** Present the script + a one-line usage note; let the maintainer commit it.
