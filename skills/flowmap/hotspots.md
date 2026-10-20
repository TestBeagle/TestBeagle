# hotspots — collecting tap targets and where they go

Shared recipe for flowmap. For each screen you need the shot, the rect of every tappable element **in that shot's pixels**, its label, and its destination. Take the rects in the same session, viewport, and scroll position as the shot — a probe at a different window size moves anything positioned against the viewport, and `build_flowmap.py` will reject rects that run outside the shot. Say in `meta.driver` which method below you used.

On every platform:
- **Add by hand what the tree misses.** Compare each screen's list with its shot. A target the method can't see (a backdrop, a disabled button, a picker, a group reported as one node) is measured from the shot or the layout in the same state and added by hand; say so in the screen's `note`.
- **Clipped targets.** Record the visible part of a target cut by the screen edge or a pinned bar, and set `clipped: true`.

## Web — Playwright, agent-browser, chrome-devtools MCP

Run this in the page right after the screenshot (`agent-browser eval "$(cat hotspots.js)"`, chrome-devtools `evaluate_script`, Playwright `page.evaluate`). Set `full` to match the shot: `true` for `screenshot --full`, `false` for a viewport shot (rects are then clipped to the viewport and anything scrolled out of it is dropped).

```js
(() => {
  const SEL = 'a[href],button,[role=button],[role=link],[role=tab],[role=menuitem],[role=checkbox],[role=switch],' +
    'input:not([type=hidden]),select,textarea,summary,[onclick],[tabindex]:not([tabindex^="-"])';
  const dpr = devicePixelRatio, full = true;  // full = rects against a full-page shot; false = the viewport shot
  const ox = full ? scrollX : 0, oy = full ? scrollY : 0, seen = new Set(), out = [];
  const hits = [...document.querySelectorAll(SEL)];
  // framework click handlers (an <a> without href, a div with a listener) only show as cursor:pointer
  for (const el of document.body.querySelectorAll('*'))
    if (getComputedStyle(el).cursor === 'pointer' && getComputedStyle(el.parentElement).cursor !== 'pointer' &&
        !hits.some(h => h.contains(el) || el.contains(h))) hits.push(el);
  for (const el of hits) {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (r.width < 1 || r.height < 1 || cs.visibility === 'hidden' || el.closest('[inert],[aria-hidden=true]')) continue;
    const pts = [[.5, .5], [.1, .1], [.9, .1], [.1, .9], [.9, .9]].map(([fx, fy]) => [r.left + r.width * fx, r.top + r.height * fy]);
    const onScreen = pts.filter(([x, y]) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight);
    if (onScreen.length && !onScreen.some(([x, y]) => el.contains(document.elementFromPoint(x, y)))) continue;  // covered (scrim, dialog)
    const what = (el.getAttribute('aria-label') || (el.getAttribute('aria-labelledby') || '').split(' ')
      .map(id => document.getElementById(id)?.innerText || '').join(' ') || el.labels?.[0]?.innerText ||
      el.innerText || el.getAttribute('title') || el.querySelector('img[alt]')?.alt || el.placeholder || '')
      .trim().replace(/\s+/g, ' ').slice(0, 80);
    const [x1, y1] = full ? [r.left + ox, r.top + oy] : [Math.max(r.left, 0), Math.max(r.top, 0)];
    const [x2, y2] = full ? [r.right + ox, r.bottom + oy] : [Math.min(r.right, innerWidth), Math.min(r.bottom, innerHeight)];
    if (x2 - x1 < 1 || y2 - y1 < 1) continue;  // outside the viewport shot
    const e = [x1, y1, x2, y2].map(v => Math.round(v * dpr)), rect = [e[0], e[1], e[2] - e[0], e[3] - e[1]];
    if (seen.has(rect.join())) continue; seen.add(rect.join());
    out.push({rect, what, css: [Math.round(r.width), Math.round(r.height)], tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role'), href: el.getAttribute('href'), type: el.getAttribute('type')});
  }
  return JSON.stringify({url: location.href, dpr, hotspots: out});
})()
```

- **Coverage**: it takes semantic controls plus the outermost `cursor: pointer` elements, which catches most framework click handlers. Compare the list with the shot anyway: a handler on an element without a pointer cursor, or a backdrop/scrim that closes a dialog, has to be added by hand after you tap it.
- **Label**: the snippet approximates the accessible name; where it differs from `agent-browser snapshot -i` / chrome-devtools `take_snapshot`, use the accessibility tree's name. An empty name is a finding candidate (icon-only, unlabeled).
- **Text fields**: a styled field (Material, MUI, a bordered box) is often taller than its bare `<input>`. When tapping the visible box focuses the input (check once per field style), record the box's rect, not the input's.
- **Small**: `css` is the size in CSS px, for your notes. The badge comes from the one threshold in `meta.small_target`; the builder applies it.
- **Headless timing**: headless Chrome may not paint frames until something asks for one, so a dialog's fade-in can be caught half-transparent. Take a throwaway screenshot, wait about a second, then take the real one. Move the pointer to an empty corner first so no hover tooltip is in the shot. Disabled buttons and very thin fields fail the hit test; measure them with `getBoundingClientRect` in the same state and add them by hand.
- **Destination**: follow Mapping destinations below. An `href` to a same-origin route is code evidence (`evidence: "code"`) until you tap it.

## Android — `uiautomator dump`

Works for native views, and for Flutter and React Native, which expose their accessibility tree there. Bounds are already in screencap pixels. Limits: Flutter and Compose often merge a group into one clickable node, disabled buttons and pickers are missing, and a dump can show a later state than the shot. For a Flutter app, prefer the semantics walk below or the repo's own walk. Otherwise take the dump right before the screenshot and check the two match (same screen title, same scroll position); add what's missing by hand.

```bash
adb exec-out screencap -p > shots/02-note.png
adb exec-out uiautomator dump /dev/tty > /tmp/ui.xml     # retry once if it says "could not get idle state" (animation running)
python3 - /tmp/ui.xml <<'EOF'
import json, re, sys, xml.etree.ElementTree as ET
raw = open(sys.argv[1], encoding="utf-8").read()
root = ET.fromstring(raw[raw.index("<?xml"):raw.rindex(">") + 1])   # drop the trailing "UI hierchary dumped to" line
out = []
for n in root.iter("node"):
    if n.get("clickable") != "true" and n.get("long-clickable") != "true":
        continue
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", n.get("bounds")))
    label = n.get("text") or n.get("content-desc") or " ".join(
        filter(None, (c.get("text") or c.get("content-desc") for c in n.iter("node")))) or ""
    out.append({"rect": [x1, y1, x2 - x1, y2 - y1], "what": label.strip()[:80],
                "long": n.get("long-clickable") == "true", "id": n.get("resource-id"), "cls": n.get("class")})
print(json.dumps(out, ensure_ascii=False, indent=1))
EOF
adb shell wm density            # dp = px / (density / 160); flag targets under 48dp
```

## iOS Simulator — XCUITest (or idb)

simctl can't tap or read the tree (`../beagle-shared/drivers-mobile.md`). Use the repo's UI test target, or add a throwaway one only if the approved plan names it. Frames are in points; multiply by the screen scale so they match `XCUIScreen.main.screenshot()`.

```swift
extension XCTestCase {
  func flowmapShot(_ app: XCUIApplication, _ id: String) throws {
    let shot = XCUIScreen.main.screenshot()
    let png = XCTAttachment(data: shot.pngRepresentation, uniformTypeIdentifier: "public.png")
    png.name = "\(id).png"; png.lifetime = .keepAlways; add(png)
    let scale = shot.image.scale
    let types: [XCUIElement.ElementType] = [.button, .link, .cell, .switch, .textField, .secureTextField,
      .searchField, .textView, .slider, .tab, .menuItem, .segmentedControl, .stepper, .image]
    var out: [[String: Any]] = []
    for t in types {
      for e in app.descendants(matching: t).allElementsBoundByIndex where e.isHittable {
        let f = e.frame
        out.append(["rect": [f.minX, f.minY, f.width, f.height].map { Int(($0 * scale).rounded()) },
                    "what": e.label.isEmpty ? e.identifier : e.label, "type": t.rawValue, "pt": [f.width, f.height]])
      }
    }
    let json = XCTAttachment(data: try JSONSerialization.data(withJSONObject: out), uniformTypeIdentifier: "public.json")
    json.name = "\(id).json"; json.lifetime = .keepAlways; add(json)
  }
}
```

Export the attachments with `xcrun xcresulttool export attachments --path Test.xcresult --output-path <dir>` (Xcode 16+); files come out under generated names, and the `manifest.json` beside them maps each to the `name` set above (`suggestedHumanReadableName`), so rename them to `shots/<id>.png`. Flag targets under 44pt (`pt`). `.image` catches tappable images; drop the ones that aren't hittable controls.

Without a UI test target, `idb ui describe-all --udid <UDID> --json` lists every element with `frame` in points, `AXLabel`, `type`, and `enabled`; scale = screenshot width ÷ the `Application` element's frame width. Tap with `idb ui tap <x> <y>` (points) to follow destinations.

## Flutter integration tests — semantics tree

Walk the semantics tree after each shot. The root node's transform carries the device pixel ratio, so a walk from the root yields physical pixels — the screenshot's pixels. (A `tester.getRect(finder)` is logical; multiply it by `view.devicePixelRatio`.)

```dart
final _hotspots = <String, List<Map<String, Object?>>>{};

List<Map<String, Object?>> _tappables(WidgetTester tester) {
  final view = tester.binding.renderViews.first;
  final screen = Offset.zero & view.flutterView.physicalSize;
  final found = <Map<String, Object?>>[];
  void visit(SemanticsNode node, Matrix4 parent) {
    final m = node.transform == null ? parent : parent.multiplied(node.transform!);
    final d = node.getSemanticsData();
    final r = MatrixUtils.transformRect(m, node.rect).intersect(screen);
    final tap = d.hasAction(SemanticsAction.tap), long = d.hasAction(SemanticsAction.longPress);
    if ((tap || long) && !d.flagsCollection.isHidden && r.width > 0 && r.height > 0) {
      final e = [r.left, r.top, r.right, r.bottom].map((v) => v.round()).toList();
      found.add({'rect': [e[0], e[1], e[2] - e[0], e[3] - e[1]], 'label': d.label,
        if (d.tooltip.isNotEmpty) 'tooltip': d.tooltip, 'tap': tap, 'longPress': long});
    }
    node.visitChildren((c) { visit(c, m); return true; });
  }
  final root = view.owner?.semanticsOwner?.rootSemanticsNode;
  if (root != null) visit(root, Matrix4.identity());
  return found;
}
// after each binding.takeScreenshot(id): _hotspots[id] ??= _tappables(tester);
// at the end: (binding.reportData ??= {})['hotspots'] = _hotspots;   → build/integration_response_data.json
```

Call `tester.ensureSemantics()` at the start of the test and dispose it at the end.

## Mapping destinations

Every hotspot's `evidence` says how its destination or action is known. There are three values and no others:

1. **`tap`** (preferred). From the screen's state, tap the target, wait for the screen to settle, take a fingerprint, match it to a shot id, then return to the same state (back, or relaunch to a deep link). On the web, tap in a throwaway tab or session on the same state. Fingerprint in this order: route/URL or route name; the screen title or app-bar text; an image hash of the shot, only for screens without changing content.
2. **`code`** when a tap isn't safe or possible. For framework behaviour (tapping outside closes a dialog, picking a choice closes its dialog), cite the app's call site that opens that widget (`showDialog(…)` in `settings_screen.dart:120`) — the framework default is what you rely on. Sources: `href`s and router links in the markup, `Navigator.push`/`go_router` config, `showDialog`/`showModalBottomSheet`, React Router/Next routes, `NavigationLink`/storyboard segues, `startActivity`/nav graphs, the click handler's source. Name what you read in `action` or `meta.driver`.
3. **`unverified`** when neither: no `to`, an `action` that says what the label suggests, and a row in `unverified`.

A target that opens something outside the app (browser, mail, system settings, OS picker) gets `to: null` and an `action` naming where it goes; its evidence is `code` when you read the link, `tap` when you followed it.

## Destructive controls

Destructive means it deletes, sends, pays, or resets: delete, remove, pay, purchase, send, submit, reset, deactivate (삭제, 빼기, 결제, 구매, 보내기, 전송, 제출, 초기화, 탈퇴). Never tap one, with one exception: the approved plan names that control and the throwaway data it acts on (seeded for the run or created by it, on a local or test instance), and you tap it on that data only. Otherwise read its effect in code (`evidence: "code"`) or mark it `unverified`. This is the only destructive-action rule; SKILL.md points here.

## Memory

An app that holds every screenshot until the run ends (Flutter's `takeScreenshot` in an integration test) can run a small device out of memory. Capture in batches — a filter on shot ids per run (`--dart-define=WALK_SHOTS=^[0-2]`, then `^[3-9]`) — and merge the shot folders and hotspot JSON afterwards. Collecting hotspots for every shot is cheap; keep that unfiltered so one run's data covers the whole walk.
