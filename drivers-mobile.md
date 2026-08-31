# drivers-mobile — iOS & Android capture recipes

Shared by bugsweep, a11ysweep, perfsweep, scriptify. **iOS and Android are always tested together** — if a check is possible on one platform and not the other, say so explicitly rather than silently covering one.

Prefer the repo's own capture scripts / deep-link "review" modes when they exist (discover them in preflight). The commands below are the generic fallback.

## Hard rules (non-negotiable)

- **Android: never launch with `adb shell monkey`.** It silently clears the rotation lock. Always `adb shell am start -n <pkg>/<activity>`.
- **Android QA installs: uninstall before install.** `adb uninstall <pkg>` then `adb install <apk>` — never `install -r` (it caches the old build and QA sees stale UI).
- **iOS builds: exit code 0 is meaningless.** A build script can print `** BUILD FAILED **` and still exit 0. Verify success by grepping the build log for `BUILD SUCCEEDED`; treat `BUILD FAILED` as failure.
- **simctl cannot tap.** There is no tap injection on the iOS Simulator. Real iOS interaction needs the repo's review/deep-link mode or an XCUITest target; otherwise flows are unverified-by-design and go in the report's "검증 불가" section — never faked.

## iOS (Simulator, macOS)

```bash
xcrun simctl list devices booted                    # find/confirm a booted sim
xcrun simctl boot "iPhone 16"                        # boot one if none
xcrun simctl bootstatus "iPhone 16" -b               # wait until booted
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
adb uninstall <pkg> 2>/dev/null || true
adb install -t app-debug.apk
adb shell cmd uimode night yes        # dark; `no` for light
# clean status bar for screenshots:
adb shell settings put global sysui_demo_allowed 1
adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb shell am start -n <pkg>/<activity> [-e reviewMode true -e reviewScreen <name> -e reviewLocale ko]
adb shell am start -a android.intent.action.VIEW -d "yourscheme://deep/link" <pkg>   # deep-link
adb exec-out screencap -p > /tmp/shot.png                                             # screenshot
adb shell screenrecord /sdcard/clip.mp4                                               # stop with Ctrl-C, then `adb pull`
```

Interaction (when a real flow must be driven): dump the layout, read element bounds, then inject input.

```bash
adb exec-out uiautomator dump /dev/tty       # bounds="[x1,y1][x2,y2]"
adb shell input tap <x> <y>
adb shell input text "hello"
adb shell input swipe <x1> <y1> <x2> <y2> 300
adb shell input keyevent KEYCODE_BACK
```

## Output

Write captures to the location `capture-output.md` resolves for this repo (repo convention first, e.g. `docs/screenshots/{light,dark}`; else the shakeout default). Name files by `screen[-state]-<locale>-<appearance>` so the report index is scannable.
