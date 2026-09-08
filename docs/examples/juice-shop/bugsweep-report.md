# bugsweep 리포트 — OWASP Juice Shop (2026-09-08)

## 환경
- 대상: OWASP Juice Shop (`github.com/juice-shop/juice-shop`) · 소스 커밋 `1618a61` (2026-08-10) · 도커 이미지 `bkimminich/juice-shop:latest` = 앱 버전 20.2.0
- 실행: `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop` · readiness: `GET /rest/admin/application-version` → `{"version":"20.2.0"}` (exit code 아님)
- OS / 런타임: macOS (darwin 25.6) 호스트, 앱은 컨테이너 내 Node
- 드라이버: agent-browser 0.37.0 (상호작용 가능) · 콘솔/네트워크/에러 캡쳐 사용
- 시드/데이터: 도커 이미지 기본 시드. 로그인 계정 `jim@juice-sh.op`(시드 제공)

## 요약
- 심각도별: Critical 0 · High 0 · Medium 1 · Low 1 · Info 1
- 커버리지: 9/41 경로(프론트 라우트 41개 중 대표 9개 + 로그인 후 basket) · 검증 불가 6
- 로그인 플로우는 실제로 구동해 성공을 확인함(아래 [MEDIUM] 없음 — 정상 동작이 근거와 함께 확인된 항목은 발견이 아니라 커버리지 표에 기록).

## 경로 커버리지
| 경로 | 상태 | 변형 | 스크린샷 | 결과 |
|------|------|------|------|------|
| `/#/` → `/#/search` | 비로그인 | 데스크탑 | `screenshots/home.png` | 정상(콘솔·네트워크 무오류) |
| `/#/search` | 비로그인 | 데스크탑 · 모바일 390px | `search.png` · `search-mobile.png` | 정상 |
| `/#/login` | 비로그인 | 데스크탑 | `login.png` | 정상 |
| `/#/register` | 비로그인 | 데스크탑 | `register.png` | 정상 |
| `/#/contact` | 비로그인 | 데스크탑 | `contact.png` | 정상 |
| `/#/about` | 비로그인 | 데스크탑 | `about.png` | 정상 |
| `/#/score-board` | 비로그인 | 데스크탑 | `score-board.png` | 정상 |
| `/#/photo-wall` | 비로그인 | 데스크탑 | `photo-wall.png` | 정상 |
| `/#/deluxe-membership` | 비로그인 | 데스크탑 | `deluxe.png` | 정상 |
| `/#/basket` | 로그인(jim) | 데스크탑 | `basket-loggedin.png` | 정상(로그인 세션 확인) |

로그인 플로우 실측: `/#/login`에서 `jim@juice-sh.op` / 시드 비밀번호를 입력·제출 → `/#/search`로 리다이렉트, `GET /rest/user/whoami` 응답 `{"user":{"id":2,"email":"jim@juice-sh.op",...}}`로 인증 세션 확인. `basket-loggedin.png`에 앱이 띄운 "You successfully solved a challenge: Login Jim" 배너와 jim 계정 장바구니(Raspberry Juice ×2, 합계 9.98¤)가 함께 찍혀 있어, 화면 렌더가 아니라 실제 로그인 상태 진입이 근거로 남음.

## 발견 항목

### [MEDIUM] 검색 입력 필드가 접근성 레이블 없이 항상 DOM에 존재 — 접근성·자동화 양쪽에 영향
- 영역·종류·확신: 프론트(공통 헤더) · 접근성/마크업 · 확실
- 위치: 모든 라우트의 상단 `mat-toolbar` 내 `input[type="text"]`(검색창, 접힘 상태에서 `tabindex="-1"`, `placeholder=""`)
- 왜(검증): agent-browser로 axe-core 4.10.2를 주입해 `axe.run` 실행. `label`(critical) 규칙이 `/#/search`·`/#/login`·`/#/register` 세 라우트 모두에서 이 입력을 지적. 접힌 검색창이 레이블·placeholder 없이 상시 렌더되어 스크린리더가 용도를 알 수 없고, 셀렉터로도 구분이 어려움. 자세한 노드는 a11ysweep 리포트 참조.
- 수정 제안: 검색 입력에 `aria-label`(예: "Search products") 부여, 접힘 상태에서는 DOM에서 제거하거나 `aria-hidden` + 포커스 제외 일관 적용.

### [LOW] 응답 헤더에 `X-Recruiting` 커스텀 헤더 노출
- 영역·종류·확신: 서버(HTTP 응답) · 정보 노출 · 확실
- 위치: 모든 응답. `GET /` 헤더에 `X-Recruiting: /#/jobs`
- 왜(검증): `curl -D -`로 확인. 기능 결함은 아니나 불필요한 커스텀 헤더로, 표면적을 넓힘. (보안 관점 상세는 breachsweep 리포트.)
- 수정 제안: 프로덕션 빌드에서 해당 헤더 제거.

### [INFO] 감사한 9개 라우트에서 콘솔 오류·실패 네트워크 요청 없음
- 영역·종류·확신: 프론트 런타임 · 관측 · 확실
- 위치: 위 커버리지 표의 라우트 전체
- 왜(검증): 각 라우트에서 `agent-browser console` / `errors` / `network requests`를 캡쳐. score-board는 하드 리로드 후에도 콘솔 0건. 네트워크는 라우트별 요청 중 non-2xx/3xx 0건(예: score-board 리로드 시 36개 요청 전부 2xx/3xx). 이는 "정상 통과"가 아니라 "이 범위에서 이 신호만 무오류"라는 관측이며, 아래 검증 불가 항목은 별개.

## 검증 불가
| 항목 | 이유 | 수동 확인 방법 |
|------|------|------|
| 회원가입 → 실제 계정 생성 제출 | 비파괴 원칙상 상태 변경 폼 미제출 | `/#/register`에서 실제 가입 후 `/#/login` 확인 |
| 결제·주문 완료(`/#/order-completion`, `/#/payment`) | 장바구니는 확인했으나 결제 플로우 미실행(부작용) | jim 로그인 후 checkout 진행 |
| 2FA(`/#/2fa/enter`, `/#/two-factor-authentication`) | 2FA 활성 계정 시드 미구성 | 2FA 등록 계정으로 로그인 |
| 관리자 화면(`/#/administration`) | 관리자 권한 세션 미확보(비파괴 범위) | admin 계정 로그인 후 접근 |
| 다국어(로케일 변형) | 이번 실행은 EN 단일 캡쳐 | 언어 메뉴로 로케일 전환 후 재캡쳐 |
| 라이트/다크 테마 변형 | 앱이 단일 테마 | 해당 없음 |

## 스크린샷·영상 인덱스
`screenshots/` 폴더. `home.png`=`search.png`(루트가 검색으로 리다이렉트) · `login.png` · `register.png` · `contact.png` · `about.png` · `score-board.png` · `photo-wall.png` · `deluxe.png` · `search-mobile.png`(390×844) · `basket-loggedin.png`(jim 로그인 상태).
