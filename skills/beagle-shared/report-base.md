# report-base — shared report skeleton & anti-slop rules

Every TestBeagle skill writes its report on this skeleton.

**Report language.** Default to Korean (the maintainer's language). Write the report in English instead when the user asks for English, or when the repo and its docs are English-first. If the user asks for a specific language you can write fluently, use that language for the whole report. Name the report's language where it isn't obvious (e.g. an "English version" line linking the default). Translate the prose and tables; never translate code, commands, identifiers, HTTP headers, file paths, or tool output — those stay verbatim as evidence. Do not claim a language you cannot write accurately; if unsure, stay in Korean or English and say so.

Each skill adds its own finding fields (see its SKILL.md); everything else here is common.

## Anti-slop rules (mandatory — the report is worthless if it reads like AI filler)

1. **Every claim is tied to evidence.** A sentence that isn't backed by a screenshot, a log line, a console/network entry, or a concrete reproduction does not belong in the report. No "should work", no "appears fine".
2. **No inflated language.** Ban filler and closers: 완벽/성공적으로/훌륭한/원활하게/전반적으로 안정적/결론적으로, "seamless", "robust", "comprehensive". State what happened, not how it felt.
3. **No emoji, no decorative headers, no restated summaries.** Say a thing once.
4. **Don't inflate the count.** One root cause = one finding, listing every location it surfaces. Three symptoms of the same bug are one finding, not three.
5. **Mark confidence.** Label each finding 확실(confirmed by reproduction) or 추정(inferred, not yet reproduced). Don't launder a guess as fact.
6. **Unverified ≠ pass.** Anything you could not exercise goes in "검증 불가", never counted as 정상. A screen that merely rendered is not a passed flow.
7. **No fix you didn't reason through.** A 수정 제안 names the actual cause and the change; "add error handling" with no target is not a suggestion.
8. **Locate the cause, not just the symptom.** Trace from where it showed up (route, request, DOM node, metric) to where it gets fixed (handler, component, middleware/config, dependency) and give `file:line` at the deepest level the evidence supports. 확실 only if you opened that line and it explains the observation (quote ≤3 lines); 추정 if you found it by search but didn't prove it (say what you searched); 미확인 if the source is unavailable or doesn't match the build that ran. Never cite a file you didn't open.
9. **One severity scale.** Critical = compromise, data loss, or a core flow broken for everyone. High = a core flow broken for some users (including assistive-tech users) or sensitive data exposed. Medium = degraded, or a barrier with a workaround. Low = minor, cosmetic, best practice. Info = observation only. The same root cause gets the same severity in every report; a report that doesn't own the issue links to the one that does instead of re-filing it.
10. **Save the evidence you cite.** Raw output you quote (logs, responses, axe/Lighthouse JSON) goes under `<report-dir>/evidence/` and is linked from the finding. Evidence that exists only in the agent's session doesn't count.
11. **Redact secrets everywhere you write** (reports, evidence, runners): passwords, tokens/JWTs, cookies, `Authorization` headers → `<redacted>`. Name where a credential came from, not its value.
12. **Coverage adds up.** Every route or screen in the inventory is either covered or listed under 검증 불가/범위 외 (grouping is fine), so the counts reconcile.

## Skeleton

```markdown
# <skill> 리포트 — <repo> (<YYYY-MM-DD>)

## 환경
- 대상: <repo path / URL>
- 소스: <path>@<git SHA> · 실행 빌드: <image revision / build id> · 일치: 예/아니오/미확인 · 빌드 모드: dev/prod
- OS / 런타임: <os>, <node/xcode/sdk versions>
- 드라이버: <driver + version>
- 시드/데이터: <seed used, app env>

## 요약
- 심각도별: Critical <n> · High <n> · Medium <n> · Low <n> · Info <n>
- 커버리지: <covered>/<total> 경로   ·   검증 불가 <n>

## 경로 커버리지
| 경로 | 상태(로그인/비로그인·empty/populated) | 변형(dark/locale) | 스크린샷 | 결과(정상/이슈/검증불가) |
|------|------|------|------|------|

## 발견 항목
<!-- one block per finding; skill-specific fields defined in its SKILL.md -->

## 검증 불가
| 항목 | 이유(도구 한계 / 환경 / 권한) | 수동 확인 방법 |
|------|------|------|

## 스크린샷·영상 인덱스
<!-- filename → 경로/상태/변형 -->
```

## Finding block (common shape)

```markdown
### [SEVERITY] <한 줄 제목>
- 영역·종류·확신: <area> · <kind> · <확실|추정>
- 증상 위치: <route / endpoint / selector / screen>
- 원인 위치: <file:line | config key | dep@ver> · <확실|추정|미확인> · <how traced: grep / stack trace / source map>
- 왜(검증): <무엇을 했고, 무엇을 관찰했는가 — 스크린샷/콘솔/네트워크 증거>
- 수정 제안: <원인 + 구체적 변경>
```
