# a11ysweep 리포트 — OWASP Juice Shop (2026-09-08)

## 환경
- 대상: OWASP Juice Shop 20.2.0 (도커 `bkimminich/juice-shop`, 소스 `1618a61`)
- 실행: `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop` · `http://localhost:3000`
- 드라이버: agent-browser 0.37.0로 렌더된 페이지에 axe-core 4.10.2를 CDN 주입(`evaluate`), `axe.run(document,{resultTypes:['violations']})` 실행. Juice Shop은 CSP가 없어 주입이 그대로 성공.
- 감사 라우트: `/#/search`, `/#/login`, `/#/register`

## 요약
- 심각도별(axe impact): Critical 1규칙 · Moderate 3규칙 · Minor 2규칙
- 커버리지: 3/41 라우트(대표) · 검증 불가 다수(아래)
- 모든 수치는 axe-core 규칙 위반 노드 수로, 규칙별로 근거를 명시.

## 경로 커버리지
| 라우트 | axe 위반 규칙 | 대표 위반 |
|------|------|------|
| `/#/search` | 6 | aria-allowed-role ×15, image-redundant-alt ×16, label ×1, landmark-* ×3, region ×3 |
| `/#/login` | 3 | label ×1, region ×13, image-redundant-alt ×1 |
| `/#/register` | 3 | label ×1, region ×16, image-redundant-alt ×1 |

## 발견 항목

### [CRITICAL] 폼 입력에 접근성 레이블 없음 (axe `label`)
- WCAG 기준: 4.1.2 Name, Role, Value / 1.3.1 · 확신: 확실
- 위치: 세 라우트 모두. 노드 타깃 `input[type="text"]` — 상단 툴바의 접힌 검색 입력(`tabindex="-1"`, `placeholder=""`, 레이블 없음)
- 왜(검증): `axe.run(document,{runOnly:['label']})`가 각 라우트에서 위반 1건 반환. 반환된 노드 HTML은 레이블·`aria-label`·placeholder가 모두 비어 있는 텍스트 입력. 스크린리더 사용자는 이 입력의 용도를 알 수 없음.
- 수정 제안: 검색 입력에 `aria-label="Search products"` 부여. 접힘 상태에서는 DOM에서 제거하거나 포커스 대상에서 완전히 제외(현재는 `tabindex="-1"`이지만 axe 접근성 트리에는 이름 없는 컨트롤로 남음).

### [MODERATE] 페이지 콘텐츠가 랜드마크 밖에 위치 (axe `region`)
- WCAG 기준: 1.3.1 (best practice) · 확신: 확실
- 위치: `/#/login` ×13, `/#/register` ×16, `/#/search` ×3. 대표 타깃 `.search-area`, 알림 카드(`.accent-notification .mdc-card .notificationMessage`)
- 왜(검증): `axe.run(...runOnly:['region'])`가 콘텐츠 블록이 `main`/`nav` 등 랜드마크에 담기지 않았다고 지적. 스크린리더의 랜드마크 내비게이션으로 건너뛸 수 없어 선형 탐색을 강요.
- 수정 제안: 주요 콘텐츠를 `<main>`으로 감싸고, 알림 영역에 적절한 role 부여.

### [MODERATE] 랜드마크 중첩·중복 (axe `landmark-complementary-is-top-level`, `landmark-unique`)
- WCAG 기준: 1.3.1 (best practice) · 확신: 확실
- 위치: `/#/search` — `landmark-complementary-is-top-level` ×2, `landmark-unique` ×1
- 왜(검증): axe가 `aside`(complementary)가 다른 랜드마크 안에 중첩되어 있고, 동일 role 랜드마크가 접근명 없이 중복된다고 반환.
- 수정 제안: complementary 랜드마크를 최상위로 올리고, 중복 랜드마크에 고유 `aria-label` 부여.

### [MINOR] 이미지 대체 텍스트가 인접 텍스트와 중복 (axe `image-redundant-alt`)
- WCAG 기준: 1.1.1 (best practice) · 확신: 확실
- 위치: `/#/search` ×16(상품 카드 이미지), `/#/login` ×1, `/#/register` ×1
- 왜(검증): axe가 이미지 `alt`가 바로 옆 텍스트(상품명 등)를 그대로 반복한다고 지적. 스크린리더가 같은 문구를 두 번 읽음.
- 수정 제안: 장식·중복 이미지의 `alt`를 비우거나(`alt=""`) 텍스트와 다른 정보만 남김.

### [MINOR] 요소에 부적절한 ARIA role (axe `aria-allowed-role`)
- WCAG 기준: 4.1.2 (best practice) · 확신: 확실
- 위치: `/#/search` ×15
- 왜(검증): axe가 해당 요소 타입에 허용되지 않는 role이 지정되었다고 반환.
- 수정 제안: 지적된 요소의 role을 요소 시맨틱에 맞게 조정하거나 제거.

## 검증 불가
| 항목 | 이유 | 수동 확인 방법 |
|------|------|------|
| 키보드 포커스 순서·포커스 링 가시성 | 이번 실행은 axe 정적 규칙 위주, Tab 순회 미수행 | `agent-browser press Tab` 반복 + `snapshot`으로 포커스 요소 추적, 포커스 링 스크린샷 |
| 로그인 이후 화면(basket/order 등) a11y | axe는 비로그인 3개 라우트만 실행 | jim 로그인 세션에서 동일 주입·실행 |
| 색 대비(수치) | 이번엔 axe 기본 규칙셋만, `color-contrast` 별도 미집계 | `axe.run(...runOnly:['color-contrast'])` 실행 |
| 나머지 38개 라우트 | 대표 3개만 감사 | 라우트별 반복 실행 |

## 참고
axe-core CLI(`@axe-core/cli`)는 별도 chromedriver가 필요해 이 환경에선 구동 실패. 대신 이미 렌더된 페이지에 라이브러리를 주입하는 방식으로 실측했고(드라이버 능력 활용), CSP가 없어 주입이 가능했다는 점 자체가 breachsweep의 관측과 맞물림.
