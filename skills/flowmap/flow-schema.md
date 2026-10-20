# flow-schema — the data behind a flowmap page

`flow.json` is the single source for the page. `assets/build_flowmap.py` checks every rule below, lists **all** violations, and refuses to build until they are fixed. The page itself never varies: the builder fills the pinned `assets/flowmap.html`, and the same `flow.json` and shots always give a byte-identical `index.html`. Write the content strings (titles, notes, actions, findings) in the report language (`../beagle-shared/report-base.md`); keep labels the app shows verbatim.

## Layout on disk

```
<out>/flowmap/
  flow.json
  shots/<screen id>.png      # one shot per screen, named by its id: .png, .jpg/.jpeg or .webp
  index.html                 # written by the builder
```

## Top level

```json
{"meta": {...}, "screens": [...], "tasks": [...], "findings": [...], "unverified": [...]}
```

### `meta` (all keys required except `lang` and `unverified_none`)

| key | example | note |
|---|---|---|
| `app` | `"Sample Notes"` | the name users see; becomes the page title (`<app> 화면 흐름`) |
| `platform` | `"android"` | `web` · `ios` · `android` · `flutter` · … |
| `device` | `"Pixel 7 emulator (API 34)"` | device, simulator, or browser + viewport |
| `viewport_px` | `[1080, 2400]` | screenshot size in px |
| `locale` | `"한국어"` | shown in the header |
| `theme` | `"라이트"` | shown in the header |
| `date` | `"2026-10-20"` | capture date |
| `driver` | `"adb uiautomator dump + screencap"` | how shots and hotspots were taken, and where destinations came from code instead of a tap |
| `start` | `["01-home"]` | screens a user lands on without a tap: the launch screen, and state variants no tap leads to (empty, offline, error, another build flavor). Every other screen needs an inbound link. |
| `small_target` | `{"min": 24, "unit": "CSS px", "px_per_unit": 2}` | the one small-target threshold for this map, picked in the plan; `px_per_unit` converts screenshot px (2 for @2x, `density/160` on Android, the screen scale on iOS). The builder badges every hotspot below `min` on either side. |
| `skill` | `"1"` | the skill version from `build_flowmap.py --version`, recorded in the plan; the builder refuses another |
| `lang` | `"ko"` | page chrome language: `ko` (default) or `en` |
| `unverified_none` | `"모든 화면과 목적지를 직접 눌러 확인했습니다."` | required only when `unverified` is empty: why nothing is missing |

The builder adds `meta.template` (the template version), per screen `img`, `w` and `h`, and per hotspot `small`; don't write them yourself.

### `screens[]`

```json
{"id": "02-note", "title": "메모 편집", "group": "메모", "note": "…",
 "back": "← 또는 시스템 뒤로: 목록으로 돌아갑니다.", "backTo": "01-notes",
 "gestures": [["시스템 뒤로", "목록으로 돌아갑니다.", "01-notes"], ["왼쪽으로 밀기", "다음 메모."]],
 "hotspots": [{"rect": [640, 28, 56, 56], "what": "삭제", "to": "03-delete-dialog", "action": "", "evidence": "tap", "long": false}]}
```

- **Screen ids** — one screen per view a user can see and act on: a route or page, a dialog, sheet or menu, and a state of a route that changes its targets (empty, loading, error, logged in, selection mode, a scrolled section with different targets). The same targets with different data are one screen. Name it `NN-name` in walk order (two digits, kebab-case); a variant of `NN` is `NNb-name`, `NNc-name`. Shots from a walk named like `light/NN-name.png` map to the id by dropping the folder; take one theme set, the one in `meta.theme`.
- `id`: file-safe, `^[A-Za-z0-9][A-Za-z0-9._~-]*$`, unique. It names the PNG and is the deep link (`index.html#02-note`), so nothing else fits in a URL fragment. A `NN-` or `NNb-` prefix shows as the list number.
- `title`, `group`, `back` required. Screens are listed in array order, grouped under each change of `group`.
- `back` says what on-screen back/✕ and system back do here — even "시스템 뒤로: 앱이 닫힙니다." `note`, `backTo` (screen id or `null`), `gestures` are optional. A gesture is `[what, effect]`, `[what, effect, to]`, or `[what, effect, to|null, kind]` with `kind` one of `gesture` (default: swipes, drags, system back, keys), `state` (a control whose destination depends on app state; `what` names the condition, e.g. `"설정 (명화 액자일 때)"`), `auto` (the screen moves by itself; `"기다리기"`), `scroll` (scrolling shows another captured state). The page badges the kind.
- `w`, `h`: leave out; the builder reads them from the shot's header (PNG IHDR, JPEG SOF, WebP VP8/VP8L/VP8X). If present they must match.

### `hotspots[]` (per screen)

| key | rule |
|---|---|
| `rect` | `[x, y, w, h]` in **screenshot pixels**, inside the shot (1 px of rounding allowed). Round the edges, then take `w = right − left`. |
| `what` | the element's label, as the app names it (accessible name, text, tooltip). `(이름 없는 영역)` / `(unlabeled)` when it has none — that is itself a finding candidate. |
| `to` | screen id the tap leads to, or `null` |
| `action` | what it does in place, or extra detail for a `to`. Required when `to` is `null`. |
| `long` | `true` when the target needs a long press |
| `clipped` | `true` when the rect is only the visible part of a target cut by the screen edge or a pinned bar. Record the visible part (taps land there); the builder gives a clipped target no small badge. |
| `evidence` | `tap` (tapped and identified), `code` (read in code or markup, an `href` included), or `unverified` (neither). An `unverified` hotspot has no `to`. The page badges `code` and `unverified`. |

Blue outline = has `to` (click jumps there); orange = `action` only.

### `tasks[]`

```json
{"name": "메모 삭제", "taps": 3, "steps": [["메모 선택", "01-notes"], ["삭제 아이콘", "02-note"], ["삭제", "03-delete-dialog"]], "note": "…"}
```

`taps` counts taps from the start screen until the task is done; text entry and system dialogs (permission prompts, OS pickers) are not counted — say so in a step (`"… (세지 않음)"`). Each step's screen id is where that tap happens, or `null`.

### `findings[]`

```json
{"sev": "mid", "title": "…", "body": "…", "shots": ["02-note"]}
```

`sev` is `high` · `mid` · `low`, mapped from the suite scale in `../beagle-shared/report-base.md` rule 9: Critical/High → `high`, Medium → `mid`, Low → `low`. Info is not a finding; put it in a screen `note`. `body` says what was done and what was observed (rule 1) and whether it is 확실 or 추정 (rule 5). `shots` cites at least one screen id.

### `unverified[]`

```json
{"what": "결제 완료 화면", "why": "실제 결제가 필요해 누르지 않았습니다."}
```

Unverified means neither tapped nor read in code (rule 6). This list holds every hotspot with `evidence: "unverified"` and every screen you could not reach, grouped as you like. It may be empty only when no hotspot is unverified, and then `meta.unverified_none` says why nothing is missing.

## Validation rules (what the builder enforces)

- The top level is an object; `tasks`, `findings`, `unverified` and each screen's `gestures` are lists when present (omitted means empty).
- `meta` has every required key; `viewport_px` and every rect hold finite numbers (no NaN or Infinity anywhere in the file); `lang` is `ko` or `en`; `start` is a non-empty list of screen ids; `small_target` is `{min, unit, px_per_unit}`.
- Screen ids are unique and file-safe; exactly one `shots/<id>.png|.jpg|.jpeg|.webp` exists and is readable.
- Every screen has a `back` line.
- Every screen is reachable from `meta.start` by following hotspot `to`, gesture targets and `backTo`. Two screens that only link to each other don't count.
- Every hotspot has `what`, a valid `rect` inside the shot, and `to` or `action`.
- Every `to`, `backTo`, gesture target, task step id, and finding shot resolves to a screen id.
- `taps` is a whole number; `sev` is `high`/`mid`/`low`; findings cite at least one shot.
- Every hotspot has `evidence`; an `unverified` one has no `to`; you don't write `small`; `long` and `clipped` are true/false.
- Gestures are 2–4 items and `kind` is `gesture`, `state`, `auto` or `scroll`.
- `meta.skill` equals the builder's skill version, and `SKILL.md`, `flow-schema.md`, `hotspots.md` match the hash pinned for that version.
- `unverified` is non-empty, or no hotspot is unverified and `meta.unverified_none` explains why.
- A shot that is cut short, damaged, or has a zero size is an error, not a crash.
- `assets/flowmap.html` matches the sha256 pinned in the builder (template version in `meta.template`).

On success it prints one summary line — `flowmap: screens N · hotspots N (nav N / action N; unverified N) · tasks N · findings N · unverified N · skill N · template N` — which the hand-over quotes.
