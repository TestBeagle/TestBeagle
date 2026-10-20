---
name: flowmap
description: Use when asked for a clickable screen-flow map of a locally runnable app — every screen captured with its tap targets marked, where each one goes, task paths with tap counts, and navigation-ease findings, as one self-contained HTML page. Triggers on "화면 흐름 지도", "화면 지도 만들어줘", "클릭하면 어디로 가는지", "screen flow map", "clickable screen map", "navigation map".
---

# flowmap

Plan-gated screen-flow map: capture every screen, mark every tap target on its screenshot, record where each one goes, and build one HTML page where clicking a target jumps to the screen it opens. The page has three tabs — 화면 (screens with hotspots, back behaviour, element table), 작업 경로 (task paths with tap counts), 발견 사항 (navigation-ease findings citing their shots). Never draws a destination it didn't tap or read in code.

Skill version: 2. `python3 <this skill>/assets/build_flowmap.py --version` prints it. The plan records it as `meta.skill`. Before Phase 4, re-read this file, `flow-schema.md` and `hotspots.md` and run `--version` again; if it changed, re-check `flow.json` against the new files first. The builder refuses a flow recorded under another version, and refuses to run when these files changed without a new version.

## Phase 0 — Discover (reuse preflight)

Run/reuse `../preflight/SKILL.md` for targets, run commands, drivers, output location, and existing capture tooling (review-mode deep links, a screens walk, an E2E suite that already reaches every screen). Build the screen inventory from **declared** sources only (router config, nav graph, screen/dialog/sheet widgets) — don't launch the app to discover screens. Which states count as their own screen, and how to name them, is in `flow-schema.md` → Screen ids.

## Phase 1 — Plan + approval gate (MANDATORY)

Present: the skill version (`--version`), the platforms you will map (every platform the repo targets, per `../beagle-shared/drivers-mobile.md`; a platform you skip is named here with the reason and later listed in `unverified`), the screen list (id · title · group · state needed · how to reach it), the hotspot method per platform from `hotspots.md` and how destinations will be mapped (tapped vs read from code), the small-target threshold for this map (one value, recorded as `meta.small_target`: 48 dp Android, 44 pt iOS, 24 CSS px web at any viewport width, phone-width captures included — no per-run choice, so two runs badge the same targets), the destructive controls and how each is handled per `hotspots.md` → Destructive controls, any batching for memory, the task paths you will count, the report language (it sets `meta.lang`), and the output folder `<out>/flowmap/`: `<out>` is the folder the user or a delegating caller names; when none is named, it is the location `../beagle-shared/capture-output.md` resolves (e.g. `docs/qa/flowmap/`). Say whether you'll offer to publish the page. Then stop per the shared gate in `../beagle-shared/approval-gate.md` (if that file is missing, still stop and wait for the user's explicit approval).

## Phase 2 — Launch & capture

Start the app (readiness by evidence; seed only if the approved plan names it). If reused tooling (a repo's screens walk, a review mode) fails, fall back to the capture method in `hotspots.md` when it stays on the approved device and inside the approved destructive scope, and say so in the hand-over; otherwise stop and report. For each screen: put it in the planned state, take the shot (`../beagle-shared/drivers-web.md` / `../beagle-shared/drivers-mobile.md`), and in the same state collect its hotspots per `hotspots.md`. Save `shots/<id>.png` and the raw hotspot JSON (`evidence/hotspots/<id>.json`). When the app holds shots in memory, capture in batches (`hotspots.md` → Memory).

## Phase 3 — Map

Write `flow.json` per `flow-schema.md`. Every content string (titles, notes, actions, back lines, tasks, findings) is in the report language, and `meta.lang` is `ko` or `en` to match (`en` for any other report language). The fixed labels below are given as Korean / English.


- **Hotspots**: one per tappable element. `what` from the label the app exposes; `action` for anything that acts in place; `long` when it needs a long press. Every hotspot records its `evidence` (`hotspots.md` → Mapping destinations): `tap` — you tapped it and identified the result; `code` — you read its destination or action in code or markup (an `href` counts); `unverified` — neither, so it has no `to`. A `to` needs `tap` or `code`. Tap every target that is safe to tap (not destructive, inside the approved scope) and use `code` only for the rest: code misses runtime state (an open search bar, a route guard), so a tap wins whenever both are possible. Don't write `small`: the builder sets it from `meta.small_target`.
- **Back**: for each screen, what on-screen back/✕ and system back do (`back`, `backTo`), and gestures (swipes, pull-down, system back) as `gestures` rows.
- **Moves that aren't one plain tap** are `gestures` rows with a `kind` (`flow-schema.md` → gestures): `state` when a control's destination depends on app state (offline, an error, already following) — label it with the condition, e.g. `"설정 (명화 액자일 때)"` / `"Settings (when a painting frame)"`; `auto` when the screen moves by itself (loading → list) — label `"기다리기"` / `"Wait"`; `scroll` when scrolling the same screen shows another captured state. A state that only the environment produces (offline, server error) goes in `meta.start` only when no screen leads to it under that condition.
- **Task paths**: the main jobs a user comes for. Tap-count rule, the same every run: start on the task's start screen with nothing open; count every tap, long press, and on-screen back until the task's result is visible; don't count text entry, keyboard keys, scrolling, or system dialogs and OS pickers (permission prompts, share sheets, photo pickers — each photo and the picker's own Add/Done included) — mark those steps `(세지 않음)` / `(not counted)` and add `+ 시스템 선택기` / `+ system picker` (or the dialog's name) to the task note. Use the shortest path a user can see without prior knowledge.
- **Findings** — walk this checklist on every screen, in this order, and file what it turns up, each citing its shots:
  - dead ends (no way back but killing the app);
  - actions reachable only by long-press, or behind a menu with no visual cue;
  - destructive actions without a confirm, and confirms on harmless actions;
  - system back behaving differently from the on-screen back or ✕;
  - back that discards input without asking;
  - tap targets the builder badges as small (below `meta.small_target`), citing that threshold. A target marked `clipped` (cut by the screen edge or a pinned bar) is not filed as small unless its full size is below the threshold;
  - icon-only buttons; unlabeled targets, especially full-screen tap areas;
  - task paths with too many taps for how often the task is done;
  - the same thing named or measured differently on different screens;
  - a feature reachable only through a misleadingly named menu.

  Severity by impact on the user, per `../beagle-shared/report-base.md` rule 9 (mapping in `flow-schema.md`). Each body states what you did and saw, and 확실/추정 (confirmed/likely).
- **Unverified** means neither tapped nor read in code — nothing else. Every hotspot with `evidence: "unverified"` and every screen you couldn't reach goes in `unverified` (grouping is fine), with the reason.

## Phase 4 — Build

```bash
python3 <this skill>/assets/build_flowmap.py <out>/flowmap/flow.json
```

It validates `flow.json` against `flow-schema.md` — types, every `to` and shot id resolves, every rect lies inside its shot, every hotspot has `to` or `action` and an `evidence`, every screen has a `back` line and is reachable from `meta.start`, `unverified` is filled or explained — reads each shot's size, sets the small-target badges, and writes `index.html` beside `shots/` from the pinned `assets/flowmap.html`. Fix every error it lists in `flow.json`, then rebuild. Shots may be PNG, JPEG or WebP; convert large sets to WebP (`cwebp -q 80`) or JPEG to keep the folder small. Open the page once at desktop and phone width and click a few blue targets before handing over. `--selftest` checks the builder itself.

## Phase 5 — Hand over

Hand over `<out>/flowmap/` (`index.html`, `shots/`, `flow.json`) and quote the builder's `flowmap:` summary line. Say whether you fell back from reused tooling to the `hotspots.md` method, and which platforms you skipped. The page has no external requests and uses relative paths, so the folder opens anywhere. Then offer to publish:

- **Claude Code with an Artifact tool**: on the user's yes, publish `index.html` as a private artifact with each shot as a supporting file at the same relative path (`files: {"shots/<file>": "<out>/flowmap/shots/<file>", …}`). The template already follows the artifact page contract (no document skeleton of its own, `<title>` first, light/dark tokens, explicit background), so publish the built file as is.
- **Codex or anywhere else**: give the local path.

Don't auto-commit; screenshots can be large or private.

## Hard rules

- **One page, every run.** Never hand-write, restyle, translate, or patch the page or `assets/flowmap.html`. The only way to make a flowmap is `build_flowmap.py` on a `flow.json`; only the data differs between runs, in Claude Code and Codex alike. If the builder can't run (no `python3`) or keeps failing, report that as the result — don't improvise a page.
- Destructive controls follow the one rule in `hotspots.md` → Destructive controls.
- A hotspot's `to` is a tap you made or code you read (`evidence` says which) — never a guess from the label. Neither → `evidence: "unverified"`, an `action`, and an `unverified` row.
- Rects come from the same state and viewport as the shot. The builder rejects rects outside the image; don't silence it by clamping.
