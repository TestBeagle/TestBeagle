#!/usr/bin/env python3
"""Build the flowmap page: validate flow.json, inline it into flowmap.html, write index.html.

Usage:
  python3 build_flowmap.py <dir>/flow.json     # reads <dir>/shots/<id>.png|jpg|webp, writes <dir>/index.html
  python3 build_flowmap.py --selftest          # builds assets/example in a temp dir and checks the output
  python3 build_flowmap.py --version           # the skill version a plan records as meta.skill

Stdlib only. Every rule in ../flow-schema.md is checked; all violations are listed, then it exits 1.
The same flow.json and shots always give a byte-identical index.html.
"""
import hashlib
import json
import math
import re
import shutil
import struct
import sys
import tempfile
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "flowmap.html"
# Bump both together, only when flowmap.html is changed on purpose (and say why in the commit).
TEMPLATE_VERSION = "3"
TEMPLATE_SHA256 = "ebb6b7d51476c4bff78ef6b8f4c4473405c2ff29ddfbf57ea258bddb426ed37d"
# The skill version: bump it, and re-pin RULES_SHA256, whenever SKILL.md, flow-schema.md or hotspots.md change.
# A plan records it as meta.skill; a build refuses a flow made under another version.
SKILL_VERSION = "2"
RULES = ("SKILL.md", "flow-schema.md", "hotspots.md")
RULES_SHA256 = "9a5dde3ca4d6b8bba0c56dd6d4f63c1aa2faac3bfe3f009786de5a63c65dd3d0"
GESTURE_KINDS = ("gesture", "state", "auto", "scroll")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]*$")  # file-safe and survives as a bare #anchor
META_TEXT = ("app", "platform", "device", "locale", "theme", "date", "driver")
SHOT_EXTS = (".png", ".jpg", ".jpeg", ".webp")
EVIDENCE = ("tap", "code", "unverified")
SMALL_MIN = {"CSS px": 24, "pt": 44, "dp": 48}  # one threshold per unit (SKILL.md Phase 1), so two runs badge the same targets
TITLE = {"ko": "{app} 화면 흐름", "en": "{app} screen flow"}
# Fixed chrome every built page must carry; a page without them did not come from this template.
FIXED_UI = ("모든 터치 영역 표시", "작업 경로", "발견 사항", "뒤로 가기", "길게 누르기", "← 뒤로", "코드로 확인", "확인 안 함", "상태에 따라",
            "Show all tap areas", "Task paths", "Findings")


def image_size(path):
    """(width, height) from the file header: PNG IHDR, JPEG SOFn, or WebP VP8/VP8L/VP8X. ValueError if unreadable."""
    data = Path(path).read_bytes()
    w = h = 0
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
    elif data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 <= len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01, 0xFF) or 0xD0 <= marker <= 0xD7:
                i += 1 if marker == 0xFF else 2
                continue
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                break
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            if seg < 2:
                raise ValueError("JPEG segment length is broken")
            i += 2 + seg
        else:
            raise ValueError("JPEG without a frame header")
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP" and len(data) >= 16:
        chunk = data[12:16]
        if len(data) < {b"VP8 ": 30, b"VP8L": 25, b"VP8X": 30}.get(chunk, 16):
            raise ValueError("WebP header is cut short")
        if chunk == b"VP8 ":
            w, h = (v & 0x3FFF for v in struct.unpack("<HH", data[26:30]))
        elif chunk == b"VP8L":
            b = struct.unpack("<I", data[21:25])[0]
            w, h = (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
        elif chunk == b"VP8X":
            w, h = 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
        else:
            raise ValueError(f"unknown WebP chunk {chunk!r}")
    else:
        raise ValueError("not a PNG, JPEG or WebP, or cut short")
    # a file cut off after its header still reads a size; the end marker shows the image data is all there
    if not (data.endswith(b"IEND\xaeB`\x82") if data[:4] == b"\x89PNG" else data.endswith(b"\xff\xd9") if data[:2] == b"\xff\xd8"
            else 8 + int.from_bytes(data[4:8], "little") <= len(data)):
        raise ValueError("is cut short (no end of image data)")
    if w <= 0 or h <= 0:
        raise ValueError(f"has a zero size ({w}x{h})")
    return w, h


def is_str(v):
    return isinstance(v, str) and v.strip() != ""


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate(flow, shots_dir):
    """Return a list of every rule violation. On success, sets each screen's img/w/h and each hotspot's small."""
    if not isinstance(flow, dict):
        return ["flow.json: the top level must be an object"]
    errs = []
    meta = flow.get("meta")
    if not isinstance(meta, dict):
        errs.append("meta: must be an object")
        meta = {}
    for k in META_TEXT:
        if not is_str(meta.get(k)):
            errs.append(f"meta.{k}: missing")
    vp = meta.get("viewport_px")
    if not (isinstance(vp, list) and len(vp) == 2 and all(is_num(v) and v > 0 for v in vp)):
        errs.append("meta.viewport_px: must be [width, height] in px")
    if meta.get("lang", "ko") not in ("ko", "en"):
        errs.append("meta.lang: must be 'ko' or 'en'")
    st = meta.get("small_target")
    if not (isinstance(st, dict) and is_num(st.get("min")) and st["min"] > 0 and is_str(st.get("unit"))
            and is_num(st.get("px_per_unit")) and st["px_per_unit"] > 0):
        errs.append("meta.small_target: must be {min, unit, px_per_unit}, e.g. {\"min\": 24, \"unit\": \"CSS px\", \"px_per_unit\": 2}")
        st = None
    elif SMALL_MIN.get(st["unit"]) != st["min"]:
        errs.append(f"meta.small_target: {st['min']} {st['unit']!r} is not the fixed threshold; use one of "
                    + ", ".join(f"{m} {u}" for u, m in SMALL_MIN.items()))
    if meta.get("skill") != SKILL_VERSION:
        errs.append(f"meta.skill: the plan recorded skill {meta.get('skill')!r}, but these files are skill {SKILL_VERSION!r}. "
                    "Re-read SKILL.md, flow-schema.md and hotspots.md, re-check flow.json against them, then set meta.skill")
    if "unverified_none" in meta and not isinstance(meta["unverified_none"], str):
        errs.append("meta.unverified_none: must be a string")

    lists = {}
    for k in ("tasks", "findings", "unverified"):  # optional; omitted means empty, anything else but a list is an error
        v = flow.get(k, [])
        if not isinstance(v, list):
            errs.append(f"{k}: must be a list")
            v = []
        lists[k] = v

    screens = flow.get("screens")
    if not isinstance(screens, list) or not screens:
        return errs + ["screens: must be a non-empty list"]
    known = []
    for s in screens:
        sid = s.get("id") if isinstance(s, dict) else None
        if isinstance(sid, str) and ID_RE.match(sid) and sid not in known:
            known.append(sid)
    edges = {sid: [] for sid in known}

    def ref(where, sid, src=None):
        """A screen-id reference; src records a navigation edge src → sid for reachability."""
        if not isinstance(sid, str):
            errs.append(f"{where}: must be a screen id string, not {type(sid).__name__}")
        elif sid not in edges:
            errs.append(f"{where}: '{sid}' is not a screen id")
        elif src in edges:
            edges[src].append(sid)

    start = meta.get("start")
    if not (isinstance(start, list) and start):
        errs.append("meta.start: must be a non-empty list of screen ids")
        start = []
    for sid in start:
        ref("meta.start", sid)
    start = [x for x in start if isinstance(x, str)]  # a bad entry is reported above; keep it out of the set lookups below

    unverified_hotspots = 0
    seen = set()
    for i, s in enumerate(screens):
        if not isinstance(s, dict):
            errs.append(f"screens[{i}]: must be an object")
            continue
        sid = s.get("id")
        at = f"screens[{i}] ({sid!r})"
        valid_id = isinstance(sid, str) and ID_RE.match(sid) is not None
        if not valid_id:
            errs.append(f"{at}.id: must match {ID_RE.pattern}")
        elif sid in seen:
            errs.append(f"{at}.id: duplicate")
        seen.add(sid if valid_id else None)
        for k in ("title", "group", "back"):
            if not is_str(s.get(k)):
                errs.append(f"{at}.{k}: missing" + (" (say what on-screen and system back do here)" if k == "back" else ""))
        if "note" in s and not isinstance(s["note"], str):
            errs.append(f"{at}.note: must be a string")
        if s.get("backTo") is not None:
            ref(f"{at}.backTo", s["backTo"], sid if valid_id else None)

        w = h = None
        if valid_id:
            found = [shots_dir / f"{sid}{ext}" for ext in SHOT_EXTS if (shots_dir / f"{sid}{ext}").is_file()]
            if not found:
                errs.append(f"{at}: no shot shots/{sid}.png|.jpg|.jpeg|.webp")
            elif len(found) > 1:
                errs.append(f"{at}: more than one shot: {', '.join(p.name for p in found)}")
            else:
                try:
                    w, h = image_size(found[0])
                except (ValueError, struct.error, OSError) as e:
                    errs.append(f"{at}: {found[0].name} {e}")
                else:
                    for k, v in (("w", w), ("h", h)):
                        if k in s and s[k] != v:
                            errs.append(f"{at}.{k}: {s[k]} but the shot is {w}x{h}")
                    s["w"], s["h"], s["img"] = w, h, f"shots/{found[0].name}"

        gestures = s.get("gestures", [])
        if not isinstance(gestures, list):
            errs.append(f"{at}.gestures: must be a list")
            gestures = []
        for j, g in enumerate(gestures):
            gat = f"{at}.gestures[{j}]"
            if not (isinstance(g, list) and len(g) in (2, 3, 4) and is_str(g[0]) and is_str(g[1])):
                errs.append(f"{gat}: must be [what, effect], [what, effect, to] or [what, effect, to|null, kind]")
                continue
            if len(g) == 4 and g[3] not in GESTURE_KINDS:
                errs.append(f"{gat}: kind must be one of {', '.join(GESTURE_KINDS)}")
            if len(g) >= 3 and g[2] is not None:
                ref(gat, g[2], sid if valid_id else None)

        hotspots = s.get("hotspots")
        if not isinstance(hotspots, list):
            errs.append(f"{at}.hotspots: must be a list")
            continue
        for j, hs in enumerate(hotspots):
            hat = f"{at}.hotspots[{j}]"
            if not isinstance(hs, dict):
                errs.append(f"{hat}: must be an object")
                continue
            if not is_str(hs.get("what")):
                errs.append(f"{hat}.what: missing")
            r = hs.get("rect")
            rect_ok = isinstance(r, list) and len(r) == 4 and all(is_num(v) for v in r)
            if not rect_ok:
                errs.append(f"{hat}.rect: must be [x, y, w, h] in screenshot px, finite numbers")
            elif r[2] <= 0 or r[3] <= 0 or r[0] < 0 or r[1] < 0:
                errs.append(f"{hat}.rect: {r} has a negative origin or an empty size")
            elif w is not None and (r[0] + r[2] > w + 1 or r[1] + r[3] > h + 1):  # 1 px: rounding
                errs.append(f"{hat}.rect: {r} runs outside the {w}x{h} shot")
            to, action, ev = hs.get("to"), hs.get("action"), hs.get("evidence")
            if ev not in EVIDENCE:
                errs.append(f"{hat}.evidence: must be one of {', '.join(EVIDENCE)}")
            if action is not None and not isinstance(action, str):
                errs.append(f"{hat}.action: must be a string")
            if to is not None:
                ref(f"{hat}.to", to, sid if valid_id else None)
                if ev == "unverified":
                    errs.append(f"{hat}: an unverified target has no 'to'; describe it in 'action' and list it in unverified")
            if to is None and not is_str(action):
                errs.append(f"{hat}: needs 'to' or 'action'")
            if ev == "unverified":
                unverified_hotspots += 1
            for k in ("long", "clipped"):
                if not isinstance(hs.get(k, False), bool):
                    errs.append(f"{hat}.{k}: must be true/false")
            if "small" in hs:
                errs.append(f"{hat}.small: set by the builder from meta.small_target; remove it")
            elif rect_ok and st and not hs.get("clipped"):  # a clipped rect is the visible part, not the target's size
                cw, ch = r[2] / st["px_per_unit"], r[3] / st["px_per_unit"]
                hs["small"] = f"{math.floor(cw + 0.5)}×{math.floor(ch + 0.5)} {st['unit']}" if min(cw, ch) < st["min"] else None
            else:
                hs["small"] = None

    # every screen must be reachable from meta.start along taps, gestures and back
    reached, queue = set(), deque(x for x in start if x in edges)
    while queue:
        cur = queue.popleft()
        if cur not in reached:
            reached.add(cur)
            queue.extend(edges[cur])
    for sid in known:
        if sid not in reached:
            errs.append(f"screen {sid}: unreachable from meta.start — add the link that leads to it, or list it in meta.start")

    for i, t in enumerate(lists["tasks"]):
        at = f"tasks[{i}]"
        if not isinstance(t, dict):
            errs.append(f"{at}: must be an object")
            continue
        if not is_str(t.get("name")):
            errs.append(f"{at}.name: missing")
        if not (isinstance(t.get("taps"), int) and not isinstance(t.get("taps"), bool) and t["taps"] >= 0):
            errs.append(f"{at}.taps: must be a whole number")
        if "note" in t and not isinstance(t["note"], str):
            errs.append(f"{at}.note: must be a string")
        steps = t.get("steps")
        if not isinstance(steps, list) or not steps:
            errs.append(f"{at}.steps: must be a non-empty list")
            continue
        for j, step in enumerate(steps):
            if not (isinstance(step, list) and len(step) in (1, 2) and is_str(step[0])):
                errs.append(f"{at}.steps[{j}]: must be [text] or [text, screenId]")
            elif len(step) == 2 and step[1] is not None:
                ref(f"{at}.steps[{j}]", step[1])

    for i, f in enumerate(lists["findings"]):
        at = f"findings[{i}]"
        if not isinstance(f, dict):
            errs.append(f"{at}: must be an object")
            continue
        if f.get("sev") not in ("high", "mid", "low"):
            errs.append(f"{at}.sev: must be high, mid or low")
        for k in ("title", "body"):
            if not is_str(f.get(k)):
                errs.append(f"{at}.{k}: missing")
        shots = f.get("shots")
        if not isinstance(shots, list) or not shots:
            errs.append(f"{at}.shots: cite at least one screen")
        else:
            for sid in shots:
                ref(f"{at}.shots", sid)

    un = lists["unverified"]
    for i, u in enumerate(un):
        if not (isinstance(u, dict) and is_str(u.get("what")) and is_str(u.get("why"))):
            errs.append(f"unverified[{i}]: must be {{what, why}}")
    if not un and unverified_hotspots:
        errs.append(f"unverified: empty, but {unverified_hotspots} hotspot(s) have evidence 'unverified'; list them")
    elif not un and not is_str(meta.get("unverified_none")):
        errs.append("unverified: empty — list what you could not reach, or say why nothing is missing in meta.unverified_none")
    return errs


def check_template(html):
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    if digest != TEMPLATE_SHA256:
        sys.exit(f"{TEMPLATE} has changed (sha256 {digest}); it is pinned at template {TEMPLATE_VERSION}.\n"
                 "Restore it, or change it on purpose and bump TEMPLATE_VERSION and TEMPLATE_SHA256 together.")


def check_rules():
    h = hashlib.sha256()
    for name in RULES:
        h.update((HERE.parent / name).read_bytes())
    if h.hexdigest() != RULES_SHA256:
        sys.exit(f"{', '.join(RULES)} changed (sha256 {h.hexdigest()}) without a new skill version (still {SKILL_VERSION}).\n"
                 "If you are running the skill, the files changed under you: stop and re-read them. "
                 "If you changed them, bump SKILL_VERSION and re-pin RULES_SHA256.")


def reject_constant(name):
    raise ValueError(f"{name} is not allowed")


def build(flow_path):
    check_rules()
    flow_path = Path(flow_path)
    try:
        flow = json.loads(flow_path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (OSError, ValueError) as e:  # JSONDecodeError is a ValueError
        sys.exit(f"{flow_path}: cannot read: {e}")
    errs = validate(flow, flow_path.parent / "shots")
    if errs:
        print(f"{flow_path}: {len(errs)} error(s)", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)
    html = TEMPLATE.read_text(encoding="utf-8")
    check_template(html)
    for k in ("tasks", "findings", "unverified"):
        flow.setdefault(k, [])
    flow["meta"]["template"] = TEMPLATE_VERSION
    title = TITLE[flow["meta"].get("lang", "ko")].format(app=flow["meta"]["app"])
    title = title.replace("&", "&amp;").replace("<", "&lt;")
    # every '<' escaped, so no string can end the <script> or open a comment inside it
    data = json.dumps(flow, ensure_ascii=False, sort_keys=True, allow_nan=False).replace("<", "\\u003c")
    out = flow_path.parent / "index.html"
    out.write_text(html.replace("/*FLOW_TITLE*/", title).replace("/*FLOW_DATA*/", data), encoding="utf-8")
    hs = [h for s in flow["screens"] for h in s["hotspots"]]
    nav = sum(1 for h in hs if h.get("to"))
    unv = sum(1 for h in hs if h["evidence"] == "unverified")
    print(f"wrote {out}")
    print(f"flowmap: screens {len(flow['screens'])} · hotspots {len(hs)} (nav {nav} / action {len(hs) - nav}; "
          f"unverified {unv}) · tasks {len(flow['tasks'])} · findings {len(flow['findings'])} · "
          f"unverified {len(flow['unverified'])} · skill {SKILL_VERSION} · template {TEMPLATE_VERSION}")
    return out


def selftest():
    # header readers on hand-made files (the bytes they read plus an end marker), and damaged files
    def riff(body):
        return b"RIFF" + len(body).to_bytes(4, "little") + body
    png = b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR" + struct.pack(">II", 720, 1480) + b"\0" * 5 + b"\0\0\0\0IEND\xaeB`\x82"
    jpeg = b"\xff\xd8\xff\xe0\x00\x10" + b"\0" * 14 + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 1480, 720) + b"\0" * 12 + b"\xff\xd9"
    vp8x = riff(b"WEBPVP8X" + b"\0" * 8 + (719).to_bytes(3, "little") + (1479).to_bytes(3, "little"))
    vp8l = riff(b"WEBPVP8L\0\0\0\0\x2f" + struct.pack("<I", 719 | (1479 << 14)))
    with tempfile.TemporaryDirectory() as tmp:
        for name, raw in (("p.png", png), ("a.jpg", jpeg), ("b.webp", vp8x), ("c.webp", vp8l)):
            (Path(tmp) / name).write_bytes(raw)
            assert image_size(Path(tmp) / name) == (720, 1480), name
        for name, raw in (("short.png", b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0"), ("zero.png", b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR" + b"\0" * 8),
                          ("short.jpg", b"\xff\xd8\xff\xc0\x00"), ("short.webp", b"RIFF\0\0\0\0WEBPVP8 "), ("empty.png", b""),
                          ("cut.png", png[:24]), ("cut.jpg", jpeg[:-2]), ("cut.webp", vp8x[:-1])):
            (Path(tmp) / name).write_bytes(raw)
            try:
                image_size(Path(tmp) / name)
            except ValueError:
                pass
            else:
                raise AssertionError(f"damaged {name} was accepted")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "flowmap"
        shutil.copytree(HERE / "example", work)
        src = json.loads((work / "flow.json").read_text(encoding="utf-8"))
        # strings that would break out of the inline <script> if '<' were not escaped
        tricky = "</script><!--<script>\"'<b>&amp;"
        src["screens"][0]["note"] += tricky
        (work / "flow.json").write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")
        out = build(work / "flow.json")
        html = out.read_text(encoding="utf-8")
        first = hashlib.sha256(html.encode("utf-8")).hexdigest()
        assert hashlib.sha256(build(work / "flow.json").read_bytes()).hexdigest() == first, "build is not deterministic"
        template = TEMPLATE.read_text(encoding="utf-8")
        assert html.count("</script>") == template.count("</script>"), "data closed the <script>"
        assert html.count("<!--") == template.count("<!--"), "data opened an HTML comment"
        assert "/*FLOW_" not in html, "placeholder left in output"
        assert html.lstrip().startswith("<title>"), "page must open with <title>"
        assert not re.search(r"<!doctype|<(html|head|body)[\s>]", html, re.I), "artifact pages carry no skeleton tags"
        assert not re.search(r"""(src|href)=["']?(https?:)?//""", html), "no external requests"
        for s in FIXED_UI:
            assert s in html, f"fixed UI string missing: {s}"
        data = json.loads(re.search(r"const DATA = (.*);\n", html).group(1))
        assert data["screens"][0]["note"].endswith(tricky), "data did not round-trip"
        assert data["meta"]["template"] == TEMPLATE_VERSION
        assert [s["id"] for s in data["screens"]] == [s["id"] for s in src["screens"]]
        for s in data["screens"]:
            assert (s["w"], s["h"]) == image_size(work / s["img"]), s["id"]

        # an English report gets the English page title
        (work / "flow.json").write_text(json.dumps({**src, "meta": {**src["meta"], "lang": "en"}}, ensure_ascii=False), encoding="utf-8")
        en = build(work / "flow.json").read_text(encoding="utf-8")
        assert en.startswith(f"<title>{src['meta']['app']} screen flow</title>"), "lang en did not give the English title"
        (work / "flow.json").write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")

        # a broken flow must fail and name every problem, not just the first
        def errors_for(mutate):
            bad = json.loads(json.dumps(src))
            mutate(bad)
            return validate(bad, work / "shots")

        def expect(mutate, *needles):
            errs = errors_for(mutate)
            for needle in needles:
                assert any(needle in e for e in errs), f"missing error: {needle}\n" + "\n".join(errs)

        def many(b):
            b["screens"][0]["hotspots"][0]["rect"] = [0, 0, 99999, 10]
            b["screens"][0]["hotspots"].append({"rect": [1, 1, 5, 5], "what": "x", "to": None, "action": None, "evidence": "tap"})
            b["screens"][1]["back"] = ""
            b["findings"][0]["shots"] = []
            b["tasks"][0]["steps"][0][1] = "no-such-screen"
            b["screens"].append({"id": "bad id", "title": "t", "group": "g", "back": "b", "hotspots": []})
            b["unverified"] = []
            b["meta"]["unverified_none"] = "x"
        expect(many, "runs outside", "needs 'to' or 'action'", "back: missing", "cite at least one screen",
               "'no-such-screen' is not a screen id", ".id: must match")

        expect(lambda b: b.update(unverified=[]), "unverified: empty")
        def unverified_target(b):
            b["unverified"] = []
            b["meta"]["unverified_none"] = "x"
            b["screens"][0]["hotspots"][0].update(to=None, action="x", evidence="unverified")
        expect(unverified_target, "hotspot(s) have evidence 'unverified'")

        # wrong types are reported, never raised
        expect(lambda b: b.update(tasks=None, findings="x", unverified={}), "tasks: must be a list", "findings: must be a list",
               "unverified: must be a list")
        expect(lambda b: b["screens"][0].update(gestures="swipe"), "gestures: must be a list")
        expect(lambda b: b["screens"][0].update(id=["x"]), ".id: must match")
        expect(lambda b: b["screens"][0]["hotspots"][0].update(to=["02-note"]), "must be a screen id string")
        expect(lambda b: b["screens"][1].update(backTo={"a": 1}), "must be a screen id string")
        expect(lambda b: b["tasks"][0]["steps"][0].__setitem__(1, 7), "must be a screen id string")
        assert validate([], work / "shots") == ["flow.json: the top level must be an object"]
        expect(lambda b: b["meta"].update(viewport_px=[float("nan"), 1]), "meta.viewport_px")
        expect(lambda b: b["screens"][0]["hotspots"][0].update(rect=[0, 0, float("inf"), 1]), "finite numbers")
        expect(lambda b: b["screens"][0]["hotspots"][0].update(evidence="guess"), ".evidence: must be one of")
        expect(lambda b: next(h for h in b["screens"][0]["hotspots"] if h["to"]).update(evidence="unverified"),
               "an unverified target has no 'to'")
        expect(lambda b: b["screens"][0]["hotspots"][0].update(small="9px"), "set by the builder")
        expect(lambda b: b["meta"]["small_target"].update(min=44), "not the fixed threshold")
        expect(lambda b: b["meta"].update(skill="0"), "meta.skill: the plan recorded skill '0'")
        expect(lambda b: b["screens"][0].update(gestures=[["밀기", "x", None, "swipe"]]), "kind must be one of")
        ok = json.loads(json.dumps(src))
        delete = next(h for h in ok["screens"][1]["hotspots"] if h["what"] == "삭제")
        delete["clipped"] = True
        assert validate(ok, work / "shots") == [] and delete["small"] is None, "a clipped target must not get a small badge"
        assert f"Skill version: {SKILL_VERSION}" in (HERE.parent / "SKILL.md").read_text(encoding="utf-8"), "SKILL.md names another version"

        # reachability is from meta.start: two screens that only link to each other do not pass
        def island(b):
            for s in b["screens"]:
                for h in s["hotspots"]:
                    if h.get("to") in ("02-note", "03-delete-dialog") and s["id"] == "01-notes":
                        h["to"], h["action"] = None, "x"
        expect(island, "screen 02-note: unreachable", "screen 03-delete-dialog: unreachable")

        # a damaged shot is a validation error
        (work / "shots" / "02-note.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        expect(lambda b: None, "02-note.png not a PNG")

        # NaN in the file is refused before validation
        (work / "flow.json").write_text('{"meta": {"x": NaN}}', encoding="utf-8")
        try:
            build(work / "flow.json")
        except SystemExit as e:
            assert "NaN is not allowed" in str(e), e
        else:
            raise AssertionError("NaN accepted")
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:] == ["--version"]:
        print(f"flowmap skill {SKILL_VERSION} · template {TEMPLATE_VERSION}")
    elif len(sys.argv) == 2:
        build(sys.argv[1])
    else:
        sys.exit(__doc__)
