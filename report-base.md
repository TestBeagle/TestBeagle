# report-base — shared report skeleton & anti-slop rules

Every shakeout skill writes its report on this skeleton. Reports default to Korean (the maintainer's language); write English only if the user or the repo's docs are English-first. Each skill adds its own finding fields (see its SKILL.md); everything else here is common.

## Anti-slop rules (mandatory — the report is worthless if it reads like AI filler)

1. **Every claim is tied to evidence.** A sentence that isn't backed by a screenshot, a log line, a console/network entry, or a concrete reproduction does not belong in the report. No "should work", no "appears fine".
2. **No inflated language.** Ban filler and closers: 완벽/성공적으로/훌륭한/원활하게/전반적으로 안정적/결론적으로, "seamless", "robust", "comprehensive". State what happened, not how it felt.
3. **No emoji, no decorative headers, no restated summaries.** Say a thing once.
4. **Don't inflate the count.** One root cause = one finding, listing every location it surfaces. Three symptoms of the same bug are one finding, not three.
5. **Mark confidence.** Label each finding 확실(confirmed by reproduction) or 추정(inferred, not yet reproduced). Don't launder a guess as fact.
6. **Unverified ≠ pass.** Anything you could not exercise goes in "검증 불가", never counted as 정상. A screen that merely rendered is not a passed flow.
7. **No fix you didn't reason through.** A 수정 제안 names the actual cause and the change; "add error handling" with no target is not a suggestion.

## Skeleton

```markdown
# <skill> 리포트 — <repo> (<YYYY-MM-DD>)

## 환경
- 대상: <repo path / URL>   커밋: <git SHA>
- OS / 런타임: <os>, <node/xcode/sdk versions>
- 드라이버: <chrome-devtools MCP | headless chrome | simctl | adb>
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
- 위치: <route / file:line / endpoint>
- 왜(검증): <무엇을 했고, 무엇을 관찰했는가 — 스크린샷/콘솔/네트워크 증거>
- 수정 제안: <원인 + 구체적 변경>
```
