# capture-output — where screenshots, video, and reports go

Shared by every skill that writes artifacts. Reuse the repo's own convention before inventing one; confirm the location in the approval gate.

## Discovery order (first match wins)

1. **Existing screenshot/media dir** in the repo — check for `docs/screenshots/`, `docs/qa/`, `screenshots/`, `__snapshots__/`, `e2e/screenshots/`, `fastlane/screenshots/`, or any dir referenced by an existing capture script. Match its sub-structure too (e.g. `docs/screenshots/{light,dark}`, `-ko` locale suffix).
2. **Existing QA/report location** — if the repo already has prior reports (e.g. `docs/qa/*.md`, `docs/*triage*.md`), put the new report beside them and reuse their naming.
3. **shakeout default** (nothing found): propose
   - screenshots → `docs/qa/screenshots/<YYYY-MM-DD>/`
   - video → `docs/qa/media/<YYYY-MM-DD>/`
   - report → `docs/qa/<skill>-<YYYY-MM-DD>.md`

## Rules

- **Propose, then confirm.** State the chosen location in the plan and let the user override before any file is written.
- **Never write outside the target repo** (no `/tmp` as a final home — capture to `/tmp` when a tool requires it, then move the file into the repo path).
- **Keep names scannable and stable**: `route[-state][-locale][-appearance].png`. Stable names let a re-run diff cleanly against the last run.
- **Don't commit blindly.** Offer the artifacts + report as a change; let the user decide what gets committed (large media may belong in the report as links, not in git).
