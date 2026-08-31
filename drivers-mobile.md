# drivers-mobile — iOS & Android capture recipes

Shared by bugsweep, a11ysweep, perfsweep, scriptify. **When a repo targets both iOS and Android, test both** — never cover one and silently skip the other; if an OS API makes a check possible on one platform only, say so. A single-platform repo is tested on the platform it has.

Prefer the repo's own capture scripts / deep-link "review" modes when they exist (discover them in preflight). The commands below are the generic fallback.

## Hard rules (non-negotiable)

- **Android: never launch with `adb shell monkey`.** It silently clears the rotation lock. Always `adb shell am start -n <pkg>/<activity>`.
- **Android QA installs: prefer a clean install.** `adb uninstall <pkg>` then `adb install <apk>` guarantees no stale app **data/state** survives to mask a bug. (`install -r` keeps app data — it does not "cache the build" — so it's fine for a quick reinstall but weaker for QA.) Uninstall is **destructive** (it erases app data): do it only when it's named in the approved plan, against a re-seedable/emulator environment.
- **iOS builds: exit code 0 is meaningless.** A build script can print `** BUILD FAILED **` and still exit 0. Verify success by grepping the build log for `BUILD SUCCEEDED`; treat `BUILD FAILED` as failure.
- **simctl cannot tap.** There is no tap injection on the iOS Simulator. Real iOS interaction needs the repo's review/deep-link mode or an XCUITest target; otherwise flows are unverified-by-design and go in the report's "검증 불가" section — never faked.

## iOS (Simulator, macOS)

```bash
xcrun simctl list devices booted                    # already booted? (commands below use the `booted` alias)
# boot one if none — resolve a UDID so a duplicated device name isn't ambiguous:
UDID=$(xcrun simctl list devices available | grep -m1 'iPhone 16 (' | grep -oE '[0-9A-F-]{36}')
xcrun simctl boot "$UDID"; xcrun simctl bootstatus "$UDID" -b   # wait until booted
xcrun simctl ui booted appearance dark               # or: light
xcrun simctl status_bar booted override --time 9:41 --batteryLevel 100 --cellularBars 4
xcrun simctl install booted /path/to/App.app
xcrun simctl launch booted <bundle-id> [-ReviewMode -ReviewScreen <name> -AppleLanguages "(ko)"]
xcrun simctl openurl booted "yourscheme://deep/link"        # deep-link to a screen
xcrun simctl io booted screenshot /tmp/shot.png            # capture (write to /tmp, then mv — daemon can't write protected dirs)
xcrun simctl io booted recordVideo /tmp/clip.mov           # Ctrl-C / SIGINT to stop
```

Read the bundle id from the built `Info.plist` (`CFBundleIdentifier`), not a hardcoded guess. Screenshot to `/tmp` then `mv` into the output dir.

## Android (Emulator or device)

```bash
adb wait-for-device
adb uninstall <pkg> 2>/dev/null || true      # ignore "not installed"; the install below must then succeed
adb install -t app-debug.apk
adb shell cmd uimode night yes               # dark; `no` for light
# clean status bar for screenshots (demo mode is persistent — the teardown below exits it):
adb shell settings put global sysui_demo_allowed 1
adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb shell am start -n <pkg>/<activity> [-e reviewMode true -e reviewScreen <name> -e reviewLocale ko]
adb shell am start -a android.intent.action.VIEW -d "yourscheme://deep/link" <pkg>   # deep-link
adb exec-out screencap -p > /tmp/shot.png                                             # screenshot (host-side)
# video: record (or run + SIGINT to stop early), then pull and remove the device file:
adb shell screenrecord --time-limit 30 /sdcard/clip.mp4
adb pull /sdcard/clip.mp4 ./clip.mp4 && adb shell rm /sdcard/clip.mp4

# teardown — leave the emulator clean for later use:
adb shell am broadcast -a com.android.systemui.demo -e command exit
adb shell cmd uimode night no
```

Interaction (when a real flow must be driven): dump the layout, read element bounds, then inject input.

```bash
adb exec-out uiautomator dump /dev/tty       # bounds="[x1,y1][x2,y2]"
adb shell input tap <x> <y>
adb shell input text "hello"
adb shell input swipe <x1> <y1> <x2> <y2> 300
adb shell input keyevent KEYCODE_BACK
```

## Performance (perfsweep)

- **Cold-start (Android)**: `adb shell am start -W -n <pkg>/<activity>` → read `TotalTime` (ms).
- **Frames / jank (Android)**: `adb shell dumpsys gfxinfo <pkg>` → janky-frame % and 90/95/99th percentile frame times.
- **CPU / energy (Android)**: `adb shell top -n 1 | grep <pkg>`; `adb shell dumpsys batterystats <pkg>`.
- **iOS**: startup and energy via `xcrun xctrace record` / Instruments where available. If that tooling isn't at hand, mark the metric 검증 불가 rather than guessing.

## Output

Write captures to the location `capture-output.md` resolves for this repo (repo convention first, e.g. `docs/screenshots/{light,dark}`; else the shakeout default). Name files by `screen[-state]-<locale>-<appearance>` so the report index is scannable.
