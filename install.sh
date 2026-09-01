#!/usr/bin/env bash
# Symlink the TestBeagle skills into your agent runtime skill dirs.
# Usage:
#   ./install.sh                      # install into Claude Code, Codex, and ~/.agents
#   ./install.sh ~/.claude/skills     # install into specific dir(s) only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/skills"
SKILLS="preflight bugsweep breachsweep a11ysweep perfsweep casewright scriptify snap repro"
SHARED="drivers-web.md drivers-mobile.md capture-output.md report-base.md emit-runner.md approval-gate.md"

targets=("$@")
default=0
if [ ${#targets[@]} -eq 0 ]; then
  default=1
  targets=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills")
fi

for dir in "${targets[@]}"; do
  mkdir -p "$dir"
  for s in $SKILLS; do ln -sfn "$SRC/$s" "$dir/$s"; done
  for f in $SHARED; do ln -sfn "$SRC/$f" "$dir/$f"; done
  echo "installed TestBeagle skills → $dir"
done

# /beagle slash command (Claude Code) + prompt (Codex), on the default full install
if [ "$default" = 1 ]; then
  mkdir -p "$HOME/.claude/commands" && ln -sfn "$ROOT/commands/beagle.md" "$HOME/.claude/commands/beagle.md"
  mkdir -p "$HOME/.codex/prompts"  && ln -sfn "$ROOT/commands/beagle.md" "$HOME/.codex/prompts/beagle.md"
  echo "installed /beagle command → ~/.claude/commands, ~/.codex/prompts"
fi
