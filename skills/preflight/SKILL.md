---
name: preflight
description: Use when starting any app QA or test run, to check whether a repo can be run and tested locally — detect project type, verify the toolchain, discover how it runs and where screenshots/media should go — before capturing or testing. Triggers on "테스트 가능한 환경인지", "환경 점검", "preflight", "can I run this locally".
---

# preflight

The foundation for every TestBeagle skill: read-only discovery that answers "can this repo be run and tested locally, and how?" before anyone launches, seeds, or captures anything. The other skills (bugsweep, breachsweep, a11ysweep, perfsweep, casewright, scriptify, snap, repro) start by reusing preflight's findings and stop if the repo isn't locally testable.

## When to use

- Before any QA/test run, or when the user asks "이 레포 테스트 가능한 환경이야?" / "how do I run this locally?"
- Standalone, to produce a testability report without running anything.

## Workflow (read-only — make no changes)

1. **Detect targets.** Classify each runnable surface: web (Vite/Next/webpack, `index.html`), iOS (`*.xcodeproj`/`*.xcworkspace`), android (`build.gradle*` + `AndroidManifest.xml`), api (server framework + health route, no UI), cli (bin/TUI entry). A monorepo yields several — enumerate all.
2. **Toolchain doctor.** For each target, check the tools it needs exist and their versions: node/pnpm/npm, Xcode + `xcrun simctl`, Android SDK `adb`, docker/compose (`docker info`, `docker image inspect <img>` for image targets), `ffmpeg` with libvpx/libx264 if video is planned, plus any repo-declared version pins. For web targets also resolve the driver per `../beagle-shared/drivers-web.md`: the repo's own E2E runner, `agent-browser --version`, a connected browser MCP, or only headless Chrome (capture-only). Record what's missing with the install command to fix it (e.g. `brew install agent-browser`).
3. **Discover how it runs.** Read `README`, `AGENTS.md`, `CLAUDE.md`, `package.json` scripts, `scripts/`, `Makefile`, `docker-compose*`. Extract the exact local-run command per target and the env it needs (API base URL, ports, `.env`).
4. **Readiness method.** Find how to know it's up by evidence: a health/ready endpoint to poll, a build-success marker to grep (never trust an exit code — some build wrappers exit 0 on failure). Note any documented gotchas.
5. **Existing tooling to reuse.** Inventory seed scripts, deep-link/"review" capture modes, existing capture scripts, and prior QA reports. Downstream skills must reuse these, not reinvent them.
6. **Output location.** Resolve where screenshots/video/reports should go via `../beagle-shared/capture-output.md` and propose it.
7. **Source access.** Record where the source lives, whether it is readable, and whether it is the version that will run (git SHA vs build/image revision, e.g. `docker image inspect <img> --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'`). List the entry points findings will be traced through: router config, server route registration, middleware/config, component directory, and whether source maps are served. If the source is missing or the versions differ, say so — downstream findings then mark cause locations 미확인.

## Output — testability report

Report, in Korean by default, using the header/anti-slop conventions in `../beagle-shared/report-base.md`:

- **판정**: 각 타깃별 로컬 테스트 가능 / 불가(부족한 것 + 설치 명령).
- **실행 계획**: 타깃별 실행 명령 · 필요한 env · readiness 확인법.
- **재사용 자산**: 발견한 시드/review-mode/캡쳐 스크립트/기존 보고서 경로.
- **제안 출력 위치**: 스크린샷·영상·리포트 경로.
- **소스 접근**: 소스 위치 · 실행 빌드와 버전 일치 여부 · 원인 추적 진입점.
- **드라이버**: 각 타깃에 쓸 드라이버(`../beagle-shared/drivers-web.md` / `../beagle-shared/drivers-mobile.md`)와 그 한계(예: simctl 탭 불가, agent-browser·브라우저 MCP 둘 다 없으면 캡쳐 전용).

Print the report in chat. Write it to `<report-dir>/preflight-<YYYY-MM-DD>.md` only when the user asks or an approved plan includes it. Downstream skills reuse a saved report when its commit matches HEAD, otherwise they re-run preflight. They gate on it: if a target is "테스트 불가", say so and don't pretend to test it.
