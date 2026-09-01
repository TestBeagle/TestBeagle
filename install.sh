#!/usr/bin/env bash
# Symlink the testbeagle skills into your agent runtime skill dirs.
# Usage:
#   ./install.sh                      # install into Claude Code, Codex, and ~/.agents
#   ./install.sh ~/.claude/skills     # install into specific dir(s) only
set -euo pipefail

TESTBEAGLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="preflight bugsweep breachsweep a11ysweep perfsweep casewright scriptify"
SHARED="drivers-web.md drivers-mobile.md capture-output.md report-base.md emit-runner.md approval-gate.md"

targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  targets=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills")
fi

for dir in "${targets[@]}"; do
  mkdir -p "$dir"
  for s in $SKILLS; do ln -sfn "$TESTBEAGLE_DIR/$s" "$dir/$s"; done
  for f in $SHARED; do ln -sfn "$TESTBEAGLE_DIR/$f" "$dir/$f"; done
  echo "installed testbeagle skills → $dir"
done
