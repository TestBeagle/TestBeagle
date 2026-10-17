# bugsweep 리포트 — OWASP Juice Shop (2026-10-11 실행 · 2026-10-17 수정)

English version: [bugsweep-report-en.md](./bugsweep-report-en.md)

## 환경
- 대상: OWASP Juice Shop · http://127.0.0.1:3100 (컨테이너 `tb-juice`, 코디네이터가 기동·정지)
- 소스: image /juice-shop@5658473 · 실행 빌드: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · 일치: 예 · 빌드 모드: prod
- OS / 런타임: macOS 27.0.1 (Darwin 27.0.0) · 컨테이너 Node(이미지 내장) · Chrome for Testing(agent-browser 번들)
- 드라이버: agent-browser 0.37.0
- 시드/데이터: 시드 없음. 테스트 계정은 정상 가입 플로우로 직접 생성(`bugsweep-<timestamp>@example.test`). 종료 시 세션 close.
- 소스 추적: 실행 빌드에 source map 없음 → 서버 번들의 고유 문자열/셀렉터를 `frontend/src`로 grep해 추적. node_modules 제거 → 라이브러리 내부 throw 지점은 열 수 없음.
- 수정 시점 제약: 2026-10-17 수정 때는 컨테이너가 정지돼 있었고 소스 사본(`scratchpad/src`)도 tmp 정리로 파일이 지워져 있었다. 아래 `file:line`은 모두 실행 중에 직접 열어 본 줄이다. 새로 추가한 F5·F6은 그 뒤 재확인을 못 했으므로 원인을 추정으로 둔다.

### 인증 상태 표기
로그인은 토큰을 localStorage와 쿠키 둘 다에 저장한다(`frontend/src/app/login/login.component.ts:102`, `:105`). 실행 중 "로그아웃"을 `localStorage.clear()`로만 해서 쿠키가 남았다. 그래서 상태를 세 가지로 나눈다.
- **A** 가입 전 세션(계정 없음, 실제 비로그인)
- **B** localStorage 토큰 없음·쿠키 토큰 잔존(혼합). 프런트 가드는 비로그인으로 보지만 서버 `whoAmI`는 계정을 돌려준다(재활용 폼 Requestor에 계정 이메일 표시).
- **C** 로그인

### 실행 중 부수효과
Juice Shop은 교육용 앱이라 특정 동작에 "챌린지 해결" 배너를 띄운다. 이번 실행에서 의도와 무관하게 배너 3개가 떴다. `#/score-board` 방문 직후 "Score Board", 그다음 `#/2fa/enter` 캡처까지 사이에 "View Basket", "Error Handling". 뒤의 둘은 그 사이에 연 `#/recycle`, `#/track-result` 중 어느 요청이 트리거했는지 기록하지 않았다(스크린샷 score-board.png, 2fa-enter.png, track-result.png 상단).

## 요약
- 심각도별: Critical 0 · High 0 · Medium 2 · Low 4 · Info 0
- 커버리지(단위: `app.routing.ts` 라우트 엔트리 47개): 정상 31 · 이슈 10 · 검증 불가 6 · 합계 47. 브라우저로 연 엔트리는 42개(정상 31 + 이슈 10 + last-login-ip 1)
- 동작까지 확인한 플로우: 회원가입(`POST /api/Users/` 201), 로그인(`POST /rest/user/login` 200, 토큰 발급), 장바구니 담기(`PUT /api/BasketItems/11` 200, Apple Juice 수량 증가), 가드 차단(administration·accounting·deluxe-membership → 403 화면). 나머지 "정상"은 렌더와 콘솔만 본 결과이며 제출·저장 같은 동작은 실행하지 않았다.
- 보안/접근성 이슈는 이 리포트에서 다루지 않는다. 각각 breachsweep-report / a11ysweep-report 소관.

## 커버리지 단위
- 단위는 `frontend/src/app/app.routing.ts`의 `routes` 배열 엔트리다. `path:` 45개(중첩 자식 포함)와 `matcher:` 2개(oauthMatcher, tokenMatcher)를 합쳐 47개. 지연 로드 모듈(`wallet-web3`, `web3-sandbox`, `bee-haven`) 내부의 하위 라우트는 별도로 세지 않고 모듈 루트로 센다.
- 엔트리가 매칭되는 URL을 열고 스크린샷과 콘솔을 확인했으면 그 엔트리를 판정한다. 부모 엔트리(`privacy-security`, `chatbot`)는 자식 URL을 열 때 함께 매칭되며, 부모 컴포넌트가 자식 화면의 셸로 렌더된다.
- `''` 경로는 최상위에 없다. `#/` 홈은 `**` 와일드카드(SearchResultComponent)가 받는다. 표의 40번 `''`는 chatbot의 기본 자식이다.
- 판정: **정상** = 스크린샷 내용이 기대와 맞고 콘솔 [error]/[warn] 없음. **이슈** = 발견 항목으로 등록. **검증 불가** = 열지 못했거나 열었어도 판정 근거가 없음.

## 경로 커버리지
| # | 엔트리 | 연 URL | 상태 | 스크린샷 | 근거 | 결과 |
|---|------|------|------|------|------|------|
| 1 | `administration` | `#/administration` | B, C(비관리자) | administration-nolocaltoken.png, administration-nonadmin.png | 가드 | 정상(403 "You are not allowed to access this page!") |
| 2 | `accounting` | `#/accounting` | B (C는 URL만 확인) | accounting-nolocaltoken.png | 가드 | 정상(403) |
| 3 | `about` | `#/about` | A | about.png | 렌더+콘솔 | 정상 |
| 4 | `address/select` | `#/address/select` | C | address-select.png | 렌더+콘솔 | 정상 |
| 5 | `address/saved` | `#/address/saved` | C | address-saved.png | 렌더+콘솔 | 정상 |
| 6 | `address/create` | `#/address/create` | C | address-create.png | 렌더+콘솔 | 정상(저장 미실행) |
| 7 | `address/edit/:addressId` | — | — | — | — | 검증 불가 |
| 8 | `delivery-method` | `#/delivery-method` | C | delivery-method.png | 렌더+콘솔 | 정상 |
| 9 | `deluxe-membership` | `#/deluxe-membership` | A, C | deluxe-loggedout.png, deluxe-loggedin.png | 가드+렌더 | 정상(A: 403 "Please login to view this page.") |
| 10 | `saved-payment-methods` | `#/saved-payment-methods` | C | saved-payment-methods.png | 렌더+콘솔 | 정상 |
| 11 | `basket` | `#/basket` | A, C | basket-loggedout.png, basket-loggedin.png | 플로우 | 정상 |
| 12 | `order-completion/:id` | — | — | — | — | 검증 불가 |
| 13 | `contact` | `#/contact` | A | contact.png | 렌더+콘솔 | 정상(제출 미실행) |
| 14 | `photo-wall` | `#/photo-wall` | A | photo-wall.png | 렌더+콘솔 | 이슈 F5 |
| 15 | `complain` | `#/complain` | A | complain-loggedout.png | 렌더+콘솔 | 정상(제출 미실행) |
| 16 | `order-summary` | `#/order-summary` | B | order-summary-nolocaltoken.png | 콘솔+네트워크 | 이슈 F4 |
| 17 | `order-history` | `#/order-history` | C | order-history.png | 렌더+콘솔 | 정상(빈 상태) |
| 18 | `payment/:entity` | `#/payment/shop` | C | payment-shop.png | 콘솔 | 이슈 F4 |
| 19 | `wallet` | `#/wallet` | C | wallet.png | 렌더+콘솔 | 정상 |
| 20 | `login` | `#/login` | A, C | login.png, login-loggedin.png | 플로우 | 정상 |
| 21 | `forgot-password` | `#/forgot-password` | A | forgot-password.png | 렌더+콘솔 | 정상(재설정 미실행) |
| 22 | `recycle` | `#/recycle` | C (A·B는 콘솔만) | recycle-loggedin.png | 콘솔 | 이슈 F1 |
| 23 | `register` | `#/register` | A | register.png | 플로우 | 정상 |
| 24 | `search` | `#/search`, `#/search?q=apple` | C | search-loggedin.png, search-query.png, search-mobile.png | 렌더+콘솔 | 정상 |
| 25 | `hacking-instructor` | `#/hacking-instructor` | B | hacking-instructor.png | 렌더+콘솔 | 정상(라우팅상 SearchResultComponent) |
| 26 | `score-board` | `#/score-board` | A | score-board.png | 렌더+콘솔 | 정상 |
| 27 | `track-result` | `#/track-result` | A | track-result.png | 렌더 | 이슈 F6 |
| 28 | `track-result/new` | `#/track-result/new` | B | track-result-new.png | 렌더 | 이슈 F6 |
| 29 | `2fa/enter` | `#/2fa/enter` | A | 2fa-enter.png | 렌더+콘솔 | 정상 |
| 30 | `privacy-security`(부모) | 31–35의 URL | C | 31–35 캡처의 셸 | 렌더 | 정상 |
| 31 | `privacy-policy` | `#/privacy-security/privacy-policy` | C | privacy-policy.png | 렌더+콘솔 | 정상 |
| 32 | `change-password` | `#/privacy-security/change-password` | C | change-password.png | 렌더+콘솔 | 정상(변경 미실행) |
| 33 | `two-factor-authentication` | `#/privacy-security/two-factor-authentication` | C | two-factor-auth.png | 렌더+콘솔 | 이슈 F2 |
| 34 | `data-export` | `#/privacy-security/data-export` | C | data-export.png | 렌더+콘솔 | 정상(요청 미실행) |
| 35 | `last-login-ip` | `#/privacy-security/last-login-ip` | C | last-login-ip.png | 렌더 | 검증 불가 |
| 36 | `juicy-nft` | `#/juicy-nft` | A | juicy-nft.png | 렌더+콘솔 | 정상 |
| 37 | `wallet-web3` | `#/wallet-web3` | B | wallet-web3.png | 렌더+콘솔 | 이슈 F3 |
| 38 | `web3-sandbox` | `#/web3-sandbox` | B | web3-sandbox.png | 렌더+콘솔 | 이슈 F3 |
| 39 | `chatbot`(부모) | `#/chatbot` | C | chatbot.png | 렌더+콘솔 | 정상 |
| 40 | `''`(chatbot 기본 자식) | `#/chatbot` | C | chatbot.png | 렌더+콘솔 | 정상(환영 화면) |
| 41 | `conversation/:id` | — | — | — | — | 검증 불가 |
| 42 | `bee-haven` | `#/bee-haven` | B | bee-haven.png | 렌더+콘솔 | 이슈 F3 |
| 43 | `coding-challenge/:challengeKey` | `#/coding-challenge/scoreBoardChallenge` | C | coding-challenge.png | 렌더+콘솔 | 정상 |
| 44 | `403` | `#/403` | A | 403.png | 렌더+콘솔 | 정상 |
| 45 | `**` | `#/` | A | home.png | 렌더+콘솔 | 정상 |
| 46 | oauthMatcher | — | — | — | — | 검증 불가 |
| 47 | tokenMatcher | — | — | — | — | 검증 불가 |

변형: 테마 변형은 없다. 앱 기본 테마가 dark라서 `set media dark/light`로 찍은 쌍이 같은 테마로 나왔고, light 테마는 캡처하지 못했다(검증 불가). 모바일 뷰포트(390x844)는 `#/search` 1장(search-mobile.png, 상태 C)뿐이다.

## 발견 항목

### F3 [Medium] web3 경로 3곳에서 화면 전체가 비고 툴바도 사라짐, `window.ethereum.on` TypeError (지갑 확장 없음)
- 영역·종류·확신: web3 기능(샌드박스/지갑/faucet) · 런타임 에러 + 빈 화면 · 증상 확실 / TypeError 원인 확실 / 빈 화면과의 인과 추정
- 증상 위치: `#/web3-sandbox`, `#/wallet-web3`, `#/bee-haven` (상태 B). 스크린샷 세 장 모두 회색 빈 화면에 스낵바 "Please install a Web3 wallet like MetaMask to proceed."만 있고 앱 툴바(메뉴·검색·장바구니)가 없다. 세 경로 모두 콘솔에 `Cannot read properties of undefined (reading 'on')`.
- 원인 위치: `frontend/src/app/web3-sandbox/web3-sandbox.component.ts:60`, `frontend/src/app/wallet-web3/wallet-web3.component.ts:54`, `frontend/src/app/faucet/faucet.component.ts:71`. 셋 다 `ngOnInit`에서 가드 없이 `window.ethereum.on('chainChanged', ...)` 호출 · 확실(TypeError) · grep + 소스 확인
  ```ts
  ngOnInit (): void {
    this.handleAuth()
    window.ethereum.on('chainChanged', this.handleChainChanged.bind(this))
  ```
- 왜(검증): 지갑 확장이 없는 브라우저에서는 `window.ethereum`이 undefined라 `.on` 호출이 TypeError로 `ngOnInit`를 중단시킨다. 콘솔 증거는 `evidence/bugsweep/web3-sandbox.console.txt`, `wallet-web3.console.txt`, `bee-haven.console.txt`. 빈 화면과 툴바 소실은 스크린샷으로 확인했다. 툴바까지 사라지는 원인이 이 TypeError인지는 소스를 더 보지 못해 추정이다. 실행 중 "본문 텍스트 길이 600자 안팎"을 근거로 "렌더된다"고 적었으나, 화면에는 아무것도 보이지 않으므로 그 판단은 철회한다. 사용자는 툴바 없이 브라우저 뒤로 가기로만 빠져나올 수 있다.
- 수정 제안: 세 파일에서 `if (window.ethereum) { window.ethereum.on(...) }`로 가드하고, 지갑이 없을 때는 툴바가 있는 일반 레이아웃 안에 안내를 띄운다.

### F4 [Medium] 배송 수단 미선택 상태로 결제/주문요약 진입 시 `GET /api/Deliverys/null` 400 + 미처리 에러
- 영역·종류·확신: 결제 플로우 · 미처리 HTTP 실패 · 확실
- 증상 위치: `#/order-summary` (상태 B), `#/payment/shop` (상태 C). 둘 다 sessionStorage에 `deliveryMethodId`가 없을 때다.
- 원인 위치: `frontend/src/app/order-summary/order-summary.component.ts:44`, `frontend/src/app/payment/payment.component.ts:143` · 확실 · grep(요청 URL과 호출부가 일치)
  ```ts
  this.deliveryService.getById(sessionStorage.getItem('deliveryMethodId')).subscribe((method) => {
    this.deliveryPrice = method.price
  })
  ```
- 왜(검증): 체크아웃 순서를 거치지 않고 두 경로를 열면 `deliveryMethodId`가 null인 채로 호출돼 `GET /api/Deliverys/null` → 400이 난다. 네트워크 로그와 `curl`로 400을 재현했다(`evidence/bugsweep/order-summary-400.txt`). `subscribe`에 error 콜백이 없어 콘솔에 미처리 ERROR로 남는다(`order-summary-nolocaltoken.console.txt`, `payment-shop.console.txt`). order-summary-nolocaltoken.png에는 Delivery 0.00으로 표시된다.
- 수정 제안: 호출 전에 `deliveryMethodId`가 null이면 요청하지 않고 배송 단계로 돌려보낸다. `subscribe`에 error 콜백을 추가한다. 두 파일이 같은 패턴이므로 같이 고친다.

### F6 [Low] id 없이 주문 추적 화면을 열면 "Search Results - undefined"와 치환 안 된 `{{bonus}}` 표시
- 영역·종류·확신: 주문 추적 · 잘못된 표시 · 증상 확실 / 원인 추정
- 증상 위치: `#/track-result` (상태 A), `#/track-result/new` (상태 B). 두 스크린샷 모두 제목이 "Search Results - undefined", "Bonus Points Earned: {{bonus}}", 배송 예정 "? Days", 주문 상품 표는 비어 있다.
- 원인 위치: `frontend/src/app/track-result/track-result.component.ts:46-47`에서 `?id=` 쿼리 파라미터가 없을 때도 그대로 조회한다 → `routes/trackOrder.ts:21-22`는 없는 주문에 `{ orderId: id }`를 만들어 돌려준다 → `track-result.component.html:9`가 orderId(문자열 "undefined")를 제목에 넣고, `:79`의 `translateParams`에 `results.bonus`가 undefined로 들어가 `{{bonus}}`가 치환되지 않는다 · 추정 · 소스 확인. `/rest/track-order/undefined` 응답은 저장하지 않았고 컨테이너가 정지돼 재확인하지 못했다.
  ```ts
  this.orderId = this.route.snapshot.queryParams.id
  this.trackOrderService.find(this.orderId).subscribe((results) => {
  ```
- 왜(검증): 정상 진입 경로(주문 내역의 추적 링크)는 `?id=`를 붙인다. 주소창에서 바로 열면 id가 없고, 위 흐름으로 존재하지 않는 주문이 정상 결과처럼 그려진다. 증거는 track-result.png, track-result-new.png.
- 수정 제안: `orderId`가 없으면 조회하지 않고 "주문 번호를 입력하세요" 상태를 보여준다. 서버는 없는 주문에 가짜 레코드 대신 404를 돌려준다.

### F5 [Low] 사진 벽의 시드 사진 1장이 깨진 이미지로 표시
- 영역·종류·확신: 사진 벽 · 이미지 로드 실패 · 증상 확실 / 원인 추정
- 증상 위치: `#/photo-wall` (상태 A). 캡션 "😼 #zatschi #whoneedsfourlegs" 항목의 이미지가 깨진 아이콘으로 나온다(photo-wall.png).
- 원인 위치: `data/datacreator.ts:335`의 시드 `imagePath`에 `#`가 들어 있다(`assets/public/images/uploads/ᓚᘏᗢ-#zatschi-#whoneedsfourlegs-1572600969477.jpg`). `frontend/src/app/photo-wall/photo-wall.component.html:16`은 이를 인코딩 없이 `<img src="{{ image.url }}">`에 넣는다(`photo-wall.component.ts:68`에서 `url: memory.imagePath`) · 추정 · 소스 확인. 브라우저는 `#` 뒤를 프래그먼트로 보고 `.../uploads/ᓚᘏᗢ-`를 요청하게 된다. 같은 이름의 파일은 빌드 산출물 `frontend/dist/frontend/assets/public/images/uploads/`에 존재함을 확인했다. 실패한 이미지 요청의 네트워크 기록은 저장하지 않았다.
- 왜(검증): 파일은 있는데 화면에서는 깨진다. URL의 `#` 외에 다른 차이를 찾지 못했다.
- 수정 제안: 템플릿에서 경로 세그먼트를 `encodeURIComponent`로 인코딩하거나, 업로드 저장 시 파일명에서 `#`를 없앤다.

### F1 [Low] localStorage에 토큰이 없을 때 `#/recycle` 로드 시 ngx-translate "Parameter key is required" 콘솔 에러
- 영역·종류·확신: 재활용 신청 폼 · 콘솔 에러 · 재현 확실 / 원인 추정
- 증상 위치: `#/recycle`. 상태 A 1/1, 상태 B 3/3, 상태 C 0/3(`evidence/bugsweep/console-isolation.txt`). 실행 중에는 "비로그인에서만"이라고 적었으나, B는 쿠키로 로그인돼 있는 상태라 조건은 "localStorage에 토큰 없음"이다(추정).
- 원인 위치: `frontend/src/app/recycle/recycle.component.html:21` `<mat-error translate>` · 추정 · grep(페이지에서 유일한 bare `translate` 디렉티브)
  ```html
  <mat-error translate>
    {{"MANDATORY_QUANTITY" | translate}}
  </mat-error>
  ```
- 왜(검증): 경로별로 콘솔을 `--clear`+reload로 격리하면 이 에러는 `#/recycle`에서만 난다. 21번째 줄은 자식이 이미 `translate` 파이프인데 요소에 bare `translate` 디렉티브까지 걸려 있어, 첫 렌더에서 디렉티브가 빈 텍스트를 키로 받는다고 본다. source map이 없고 node_modules가 제거돼 라이브러리 throw 지점은 열지 못했다. 증거는 `evidence/bugsweep/recycle-translate-error.txt`(상태 B), `recycle-loggedout.console.txt`(상태 A). 상태 A의 화면 캡처는 없다(검증 불가 참조).
- 수정 제안: `<mat-error translate>`에서 bare `translate` 디렉티브를 뺀다(`<mat-error>`).

### F2 [Low] 2FA 설정 화면 로드 시 angularx-qrcode "qrdata is empty" 콘솔 에러, 캡처에 QR 없음
- 영역·종류·확신: 2단계 인증 설정 · 콘솔 에러 · 재현 확실
- 증상 위치: `#/privacy-security/two-factor-authentication` (상태 C, 2FA 미설정 계정의 설정 폼). 3/3 재현. two-factor-auth.png에는 "Scan the QR code" 안내만 있고 QR 이미지가 보이지 않는다.
- 원인 위치: `frontend/src/app/two-factor-auth/two-factor-auth.component.html:52-56` `<qrcode [qrdata]="totpUrl" ...>`. `totpUrl`은 초기값이 없고(`two-factor-auth.component.ts:58` `public totpUrl?: string`) 설정 API 응답 콜백(ts:73-78)에서야 채워진다 · 확실 · grep + 컴포넌트 소스 확인
- 왜(검증): 템플릿이 가드 없이 `totpUrl`을 바인딩하므로 첫 렌더에서 빈 값이 들어가고 angularx-qrcode가 "Field `qrdata` is empty"를 로그한다. 증거는 `evidence/bugsweep/2fa-qrcode-error.txt`, `two-factor-auth.console.txt`. 데이터가 도착한 뒤 QR이 그려지는지, 설정을 끝까지 완료할 수 있는지는 확인하지 못했다(검증 불가).
- 수정 제안: `<qrcode>`를 `@if (totpUrl)`로 감싸거나 `[qrdata]="totpUrl ?? ''" [allowEmptyString]="true"`로 바꾼다.

## 검증 불가
엔트리 6개(표의 7, 12, 35, 41, 46, 47)와 엔트리가 아닌 확인 항목을 함께 적는다.

| 항목 | 이유 | 수동 확인 방법 |
|------|------|------|
| #7 `address/edit/:addressId` | 저장된 주소 id 필요. 이번 실행에서 주소를 만들지 않음 | 주소 생성 후 그 id로 편집 경로 열기 |
| #12 `order-completion/:id` | 결제까지 마친 주문 id 필요 | 체크아웃(주소→배송→결제) 완료 후 완료 화면 열기 |
| #35 `last-login-ip` | 화면은 열렸고 "IP Address 0.0.0.0"이 표시됨. 기대값을 정한 소스를 열지 못했고 컨테이너가 정지돼 재확인 불가 | 로그아웃 후 재로그인하고 표시 IP를 실제 접속 IP와 비교 |
| #41 `chatbot/conversation/:id` | 대화 id 필요. 챗봇 대화를 시작하지 않음 | 챗봇에서 대화 시작 후 생성된 id로 열기 |
| #46 oauthMatcher (`#access_token=`) | OAuth 리다이렉트 프래그먼트 필요. 외부 IdP 없음 | 실제 OAuth 로그인 리다이렉트로 진입 |
| #47 tokenMatcher | 난독화된 특정 경로에만 매칭되는 매처. 일반 내비게이션으로 도달하지 않음 | 해당 경로를 구성해 열기 |
| 2FA QR 렌더링·설정 완료(#33) | 캡처에 QR이 없고, 설정 완료(비밀번호+초기 토큰 입력)는 실행하지 않음. 컨테이너 정지로 재확인 불가 | 2FA 설정 화면에서 QR 표시를 기다린 뒤 인증 앱으로 스캔해 토큰 입력·저장 |
| `#/recycle` 비로그인 화면(#22) | 상태 A 캡처는 없고, 상태 B 캡처는 상태 C와 바이트 단위로 같아 삭제함 | 쿠키와 localStorage를 모두 지운 세션에서 캡처 |
| `#/accounting` 로그인(비회계) 화면(#2) | URL만 확인하고 스크린샷 없음 | 로그인 상태로 열어 403 화면 확인 |
| 테마 변형(light/dark) | 앱 기본 테마가 dark라서 `set media`를 바꿔도 같은 화면. light 캡처 없음 | 앱 내 테마 전환 수단이 있으면 그것으로 전환 후 캡처 |
| 챌린지 배너 "View Basket", "Error Handling"의 트리거 요청 | 해당 구간의 네트워크를 저장하지 않음 | 새 컨테이너에서 `#/recycle`, `#/track-result`를 하나씩 열며 네트워크 기록 |
| 서버/API 라우트(`server.ts`): `/ftp`, `/support/logs`, `/file-upload`, `/profile`, `/snippets/*`, `/metrics`, `/b2b/v2`, `/dataerasure`, `/redirect`, `/promotion`, `/video`, `/api/*`, `/rest/*` | 커버리지 단위(`app.routing.ts`) 밖의 API/정적 엔드포인트. 기능 QA(브라우저 플로우) 범위 밖이며 엔드포인트 점검은 breachsweep 소관 | breachsweep-report 참조 |

## 스크린샷·영상 인덱스
전체 매핑은 [screenshots/INDEX.md](./screenshots/INDEX.md). 영상은 없다. register-filled.png(가입 폼 입력 상태)는 보안 질문 답이 보여서 삭제했다. 이 답은 비밀번호 재설정에 쓰인다(`routes/resetPassword.ts:41`).
