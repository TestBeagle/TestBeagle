# a11ysweep 리포트 — OWASP Juice Shop (2026-10-11)

> 영어판: [`a11ysweep-report-en.md`](./a11ysweep-report-en.md). 같은 실행, 같은 발견 항목.

## 환경
- 대상: OWASP Juice Shop, 로컬 컨테이너 `tb-juice` · `http://127.0.0.1:3100`
- 소스: image /juice-shop@5658473 · 실행 빌드: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · 일치: 예 · 빌드 모드: prod
- 원인 추적 경로는 저장소 루트 기준(`frontend/src/app/...`). 이미지에서 꺼낸 읽기 전용 사본을 열어 확인.
- OS: macOS (Darwin 27.0.0)
- 드라이버: agent-browser 0.37.0 · axe-core 4.12.1(agent-browser 내장, `agent-browser a11y`)
- axe 실행: 경로마다 `agent-browser a11y --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa --json`, 이어서 `--tags best-practice --json`을 따로 실행. best-practice 규칙에는 WCAG 기준을 붙이지 않음.
- 시드/데이터: 별도 시드 없음. 정상 회원가입 화면으로 만든 자체 계정 `a11y-1791729257@example.test`로 로그인(`/rest/user/whoami`가 이 이메일을 반환하는 것으로 확인). 장바구니 채운 상태를 보려고 이 계정 장바구니에 상품 2개(Apple Juice, Apple Pomace)를 담음. bugsweep·breachsweep이 같은 인스턴스에서 동시에 돌았고, 화면에 보이는 챌린지 해결 알림은 그쪽 실행에서 나온 것.
- 심각도는 report-base 규칙 9(사용자에게 미치는 영향)로 매기고, axe의 impact 값은 따로 적음.

## 요약
- 심각도별: Critical 0 · High 1 · Medium 8 · Low 8 · Info 0
- 커버리지: 16/45 경로 감사(비로그인 7, 로그인 9) · 범위 외 29 · 검증 불가 항목은 아래 표
- 키보드 순회: `/#/login`, `/#/search`(상품 목록)

## 경로 커버리지
경로 목록은 `frontend/src/app/app.routing.ts`의 `path:` 45개(하위 경로, `**` 포함).

| 경로 | 상태 | axe WCAG 위반 규칙 | axe best-practice 위반 규칙 | 증거 | 결과 |
|------|------|------|------|------|------|
| `/#/search` | 비로그인, 첫 방문(환영 대화상자·쿠키 배너 열림) | color-contrast | aria-dialog-name | [wcag](./evidence/a11ysweep/home-welcome-wcag.json) · [bp](./evidence/a11ysweep/home-welcome-bp.json) · [png](./evidence/a11ysweep/home-welcome.png) | 이슈 |
| `/#/search` | 비로그인, 배너 닫음 | color-contrast, label | aria-allowed-role, image-redundant-alt, landmark-unique, region | [wcag](./evidence/a11ysweep/home-wcag.json) · [bp](./evidence/a11ysweep/home-bp.json) | 이슈 |
| `/#/search` | 로그인 | color-contrast, label | 위와 같음 | [wcag](./evidence/a11ysweep/search-loggedin-wcag.json) · [bp](./evidence/a11ysweep/search-loggedin-bp.json) | 이슈 |
| `/#/login` | 비로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/login-wcag.json) · [bp](./evidence/a11ysweep/login-bp.json) | 이슈 |
| `/#/register` | 비로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/register-wcag.json) · [bp](./evidence/a11ysweep/register-bp.json) | 이슈 |
| `/#/forgot-password` | 비로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/forgot-password-wcag.json) · [bp](./evidence/a11ysweep/forgot-password-bp.json) | 이슈 |
| `/#/contact` | 비로그인 | label ×2 | image-redundant-alt, region | [wcag](./evidence/a11ysweep/contact-wcag.json) · [bp](./evidence/a11ysweep/contact-bp.json) | 이슈 |
| `/#/about` | 비로그인 | image-alt, label, link-in-text-block, scrollable-region-focusable | image-redundant-alt, region | [wcag](./evidence/a11ysweep/about-wcag.json) · [bp](./evidence/a11ysweep/about-bp.json) | 이슈 |
| `/#/photo-wall` | 비로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/photo-wall-wcag.json) · [bp](./evidence/a11ysweep/photo-wall-bp.json) | 이슈 |
| `/#/basket` | 로그인, 비어 있음 | aria-required-children, color-contrast, label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/basket-loggedin-wcag.json) · [bp](./evidence/a11ysweep/basket-loggedin-bp.json) | 이슈 |
| `/#/basket` | 로그인, 상품 있음 | aria-required-children, button-name, color-contrast, label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/basket-populated-loggedin-wcag.json) · [bp](./evidence/a11ysweep/basket-populated-loggedin-bp.json) · [png](./evidence/a11ysweep/basket-heading-contrast.png) | 이슈 |
| `/#/address/saved` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/address-saved-loggedin-wcag.json) · [bp](./evidence/a11ysweep/address-saved-loggedin-bp.json) | 이슈 |
| `/#/address/create` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/address-create-loggedin-wcag.json) · [bp](./evidence/a11ysweep/address-create-loggedin-bp.json) | 이슈 |
| `/#/order-history` | 로그인, 주문 없음 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/order-history-loggedin-wcag.json) · [bp](./evidence/a11ysweep/order-history-loggedin-bp.json) | 이슈 |
| `/#/saved-payment-methods` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/saved-payment-methods-loggedin-wcag.json) · [bp](./evidence/a11ysweep/saved-payment-methods-loggedin-bp.json) | 이슈 |
| `/#/complain` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/complain-loggedin-wcag.json) · [bp](./evidence/a11ysweep/complain-loggedin-bp.json) | 이슈 |
| `/#/wallet` | 로그인 | label | heading-order, image-redundant-alt, region | [wcag](./evidence/a11ysweep/wallet-loggedin-wcag.json) · [bp](./evidence/a11ysweep/wallet-loggedin-bp.json) | 이슈 |
| `/#/privacy-security/change-password` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/privacy-security-change-password-loggedin-wcag.json) · [bp](./evidence/a11ysweep/privacy-security-change-password-loggedin-bp.json) | 이슈 |
| `/#/deluxe-membership` | 로그인 | label | image-redundant-alt, region | [wcag](./evidence/a11ysweep/deluxe-membership-loggedin-wcag.json) · [bp](./evidence/a11ysweep/deluxe-membership-loggedin-bp.json) | 이슈 |
| 나머지 29개 | — | — | — | — | 범위 외(아래 검증 불가 표) |

## 발견 항목

### [High] 장바구니 수량 −/+ 버튼과 삭제 버튼에 접근 가능한 이름이 없음
- WCAG 기준: 4.1.2 Name, Role, Value (A) · axe `button-name`, impact critical
- 영역·종류·확신: 장바구니 · 레이블 누락 · 확실
- 증상 위치: `/#/basket`(로그인, 상품 있음), 상품 행마다 3개. axe 타깃 `.content-align.cdk-column-quantity.mat-column-quantity > .mdc-icon-button.mat-mdc-icon-button[mat-icon-button=""]:nth-child(1)`, 같은 경로 `:nth-child(3)`, `.cdk-column-remove.mat-column-remove > .mdc-icon-button.mat-mdc-icon-button[mat-icon-button=""]`
- 원인 위치: `frontend/src/app/purchase-basket/purchase-basket.component.html:31`, `:35`, `:51` · 확실 · `mat-column-remove`와 `(click)="delete(` 로 grep. 세 버튼 모두 Font Awesome 아이콘(`<i class="fas fa-minus-square">`, `fa-plus-square`, `far fa-trash-alt`)만 들어 있고 `aria-label`이 없음.
  ```html
  <button mat-icon-button (click)="dec(element.BasketItem.id)"><i class="fas fa-minus-square"></i></button>
  <button mat-icon-button (click)="delete(element.BasketItem.id)"><i class="far fa-trash-alt"></i></button>
  ```
- 왜(검증): axe가 상품 1개 장바구니에서 3개 노드를 보고. `agent-browser snapshot -i` 접근성 트리에서 세 버튼이 모두 이름 없이 `button`으로만 나옴([basket-populated-snapshot.txt](./evidence/a11ysweep/basket-populated-snapshot.txt)). 스크린리더 사용자는 수량을 줄이는 버튼과 상품을 지우는 버튼을 구별할 수 없어, 수량을 바꾸려다 상품을 삭제할 수 있음.
- 수정 제안: 세 버튼에 상품명을 포함한 `aria-label` 추가(예: `[attr.aria-label]="'Decrease quantity of ' + element.name"`, 삭제 버튼은 `'Remove ' + element.name`). 아이콘 `<i>`에는 `aria-hidden="true"`.

### [Medium] 상품 목록에서 어떤 컨트롤도 상품명을 이름으로 갖지 않음
- WCAG 기준: 2.5.3 Label in Name (A), 2.4.6 Headings and Labels (AA) · axe WCAG 태그 실행에서는 해당 규칙 없음(수동 확인)
- 영역·종류·확신: 상품 목록 · 레이블 · 확실
- 증상 위치: `/#/search`(로그인·비로그인). 상품 카드 `app-product:nth-child(n) > mat-card > article > section` 15개, `button.btn-basket` 15개
- 원인 위치: `frontend/src/app/product/product.component.html:22-28`(카드), `:59-61`(Add to Basket) · 확실 · 접근성 트리에 나온 문구 `Click for more information about the product`로 grep.
  ```html
  role="button"
  (click)="showDetail(product)"
  aria-label="Click for more information about the product"
  ```
- 왜(검증): 접근성 트리에서 카드 버튼 15개의 이름이 모두 `Click for more information about the product`, 담기 버튼 15개가 모두 `Add to Basket`([search-loggedin-snapshot.txt](./evidence/a11ysweep/search-loggedin-snapshot.txt)). 화면에 보이는 상품명(예: "Apple Juice (1000ml)")은 고정 `aria-label`에 덮여 이름에 들어가지 않음([label-in-name-scan.txt](./evidence/a11ysweep/label-in-name-scan.txt)). 스크린리더 사용자는 Tab으로 이동할 때 어느 상품인지 들을 수 없고, 음성 입력 사용자는 "Apple Juice 클릭"으로 카드를 열 수 없음. 우회 방법은 있음: 카드에서 Enter를 누르면 상세 대화상자가 열리고 대화상자 안에 상품명이 나오며, Escape로 닫으면 포커스가 카드로 돌아옴(직접 확인).
- 같은 요소에서 나온 best-practice 규칙(WCAG 기준 없음): `aria-allowed-role` ×15(impact minor, `<section>`에 `role="button"`), `landmark-unique` ×1(impact moderate).
- 수정 제안: `<section role="button">`을 `<button>`으로 바꾸고 고정 `aria-label`을 지워 상품명이 이름이 되게 함. 담기 버튼은 `[attr.aria-label]="('ADD_BASKET' | translate) + ': ' + product.name"`처럼 상품명 포함.

### [Medium] 상단 검색 입력란에 레이블이 없음(모든 경로)
- WCAG 기준: 4.1.2 Name, Role, Value (A) · axe `label`, impact critical
- 영역·종류·확신: 상단 바 검색 · 레이블 누락 · 확실
- 증상 위치: 감사한 16개 경로 모두. axe 타깃 `input`, `input[type="text"]`, `input[autocapitalize="none"]`, `.ng-valid`(경로마다 셀렉터만 다르고 같은 노드: `<input type="text" autocapitalize="none" placeholder="" ...>`)
- 원인 위치: `frontend/src/app/mat-search-bar/mat-search-bar.component.html:8-11` · 확실 · axe가 보고한 `autocapitalize="none"`로 grep. 이름은 바깥 호스트 요소에만 있음: `frontend/src/app/navbar/navbar.component.html:24-25`(`<app-mat-search-bar ... aria-label="Click to search">`). 입력란 자체에는 `aria-label`이 없고 `placeholder`는 `input('')` 기본값(`mat-search-bar.component.ts:33`)이라 비어 있음.
  ```html
  <input #input type="text" [(ngModel)]="value" [placeholder]="placeholder()"
      autocapitalize="none" [tabindex]="searchVisible ? 0 : -1" />
  ```
- 왜(검증): 접힌 상태에서 axe가 경로마다 1건 보고. "Open search" 버튼을 눌러 검색을 연 뒤에도 포커스가 간 입력란은 `tabindex="0"`인데 이름이 없음: 접근성 트리 `textbox`(이름 없음), 열린 상태에서 `--selector '#searchQuery'`로 다시 돌린 axe도 `label` critical 1건([search-open-wcag.json](./evidence/a11ysweep/search-open-wcag.json)). 스크린리더는 "편집 텍스트"로만 읽음. 직전에 누른 버튼이 "Open search"라 맥락으로 짐작은 가능.
- 수정 제안: `mat-search-bar.component.html`의 `<input>`에 `aria-label`(예: `[attr.aria-label]="'Search products'"` 또는 번역 키) 추가. 호스트 요소의 `aria-label`은 지움(아래 검증 불가의 `aria-prohibited-attr`도 같이 해소).

### [Medium] 보이는 레이블과 접근 가능한 이름이 다름(음성 입력으로 조작 불가)
- WCAG 기준: 2.5.3 Label in Name (A) · axe 기본 규칙에 해당 규칙 없음(수동 확인)
- 영역·종류·확신: 상단 바, 로그인, 회원가입, 고객 의견 · 레이블 · 확실
- 증상 위치와 원인 위치(모두 템플릿의 하드코딩 `aria-label`, 해당 문자열로 grep, 확실):
  | 보이는 텍스트 | 접근 가능한 이름 | 경로 | 원인 |
  |------|------|------|------|
  | OWASP Juice Shop(로고 버튼) | Back to homepage | 전체 | `frontend/src/app/navbar/navbar.component.html:15` |
  | Your Basket | Show the shopping cart | 전체 | `frontend/src/app/navbar/navbar.component.html:103-104` |
  | Log in | Login | `/#/login` | `frontend/src/app/login/login.component.html:63` |
  | Remember me | Checkbox to stay logged in or not logged in | `/#/login` | `frontend/src/app/login/login.component.html:71` |
  | Repeat Password | Field to confirm the password | `/#/register` | `frontend/src/app/register/register.component.html:50-51` |
  | Register | Button to complete the registration | `/#/register` | `frontend/src/app/register/register.component.html:117-120` |
  | Submit | Button to send the review | `/#/contact` | `frontend/src/app/contact/contact.component.html:65-67` |
- 왜(검증): 페이지에서 `aria-label`이 있는 보이는 컨트롤마다 보이는 텍스트(또는 `mat-label`)가 이름에 들어 있는지 비교한 스크립트 결과([label-in-name-scan.txt](./evidence/a11ysweep/label-in-name-scan.txt)). 음성 입력 사용자가 화면에 보이는 대로 "Log in 클릭", "Remember me 클릭"이라고 말해도 해당 컨트롤이 잡히지 않음. 쿠키 배너의 "Me want it!"/"But me wait!"도 같은 유형이나 cookieconsent 라이브러리가 넣은 이름이라 위 표에서 뺐음.
- 수정 제안: 보이는 텍스트로 충분한 버튼은 `aria-label`을 지움. 설명을 덧붙여야 하면 보이는 텍스트로 시작하게 함(예: "Remember me", "Your Basket").

### [Medium] 고객 의견 폼의 별점 슬라이더 입력에 이름이 없음
- WCAG 기준: 4.1.2 Name, Role, Value (A) · axe `label`, impact critical
- 영역·종류·확신: 고객 의견 · 레이블 누락 · 확실
- 증상 위치: `/#/contact`, axe 타깃 `.mdc-slider__input`(`<input type="range" matsliderthumb ... aria-valuetext="1★">`)
- 원인 위치: `frontend/src/app/contact/contact.component.html:38-40` · 확실 · `mat-slider` 로 grep. 이름이 `<mat-slider>` 호스트(39행)에만 있고 실제 포커스를 받는 `<input matSliderThumb>`(40행)에는 없음. 38행 `<label class="rating-label">`은 `for`가 없어 어디에도 연결되지 않음.
- 왜(검증): axe가 `.mdc-slider__input`을 `label` 위반으로 보고([contact-wcag.json](./evidence/a11ysweep/contact-wcag.json)). 제출 버튼은 별점 없이는 비활성(`!rating`, 66행)이라 이 슬라이더는 필수 입력. 스크린리더는 "슬라이더 1★"만 읽음.
- 수정 제안: `<input matSliderThumb aria-label="Rating">` 또는 `<label id="rating-label">` + `aria-labelledby="rating-label"`.

### [Medium] 쿠키 동의 배너 텍스트·링크·버튼 대비 부족
- WCAG 기준: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- 영역·종류·확신: 쿠키 배너(첫 방문 모든 경로) · 대비 · 확실
- 증상 위치: `/#/search` 첫 방문. axe 타깃 `#cookieconsent\:desc`, `.cc-link`, `.cc-btn`
- 원인 위치: `frontend/src/index.html:19-23` · 확실 · `cookieconsent`로 grep. 팔레트가 `var(--theme-primary)` 배경에 `var(--theme-text)` 글자. `--theme-primary`는 `frontend/src/styles.scss:100-101`(primary 톤 60, 계산값 `#438fff`), `--theme-text`는 `styles.scss:350`(`#e8ecef`).
- 왜(검증): axe 값과 계산 색상이 일치:
  | 요소 | 글자 | 배경 | 대비 | 기준 |
  |------|------|------|------|------|
  | 안내 문구(16px) | `#e8ecef` | `#438fff` | 2.67:1 | 4.5:1 |
  | "But me wait!" 링크(16px, `opacity` 0.8 적용 후) | `#67d033` | `#438fff` | 1.61:1 | 4.5:1 |
  | "Me want it!" 버튼(14.4px 굵게) | `#e8ecef` | `#50a400` | 2.66:1 | 4.5:1 |

  계산은 페이지의 `getComputedStyle`로 직접 함(링크는 opacity 적용 전 1.87:1, 적용 후 axe와 같은 1.61:1). 스크린샷: [cookie-banner-contrast.png](./evidence/a11ysweep/cookie-banner-contrast.png). 저시력 사용자가 처음 방문할 때 무엇에 동의하는지 읽기 어려움. 버튼을 눌러 닫으면 다시 나오지 않음.
- 수정 제안: `index.html` 팔레트를 대비가 맞는 값으로 고정(예: 배경 `--theme-background-dark` `#303030`에 글자 `#e8ecef`, 버튼은 `#e8ecef` 대신 `#000` 글자). 링크는 배경과 4.5:1 이상인 색으로.

### [Medium] Add to Basket·Checkout 버튼의 키보드 포커스가 거의 보이지 않음
- WCAG 기준: 2.4.7 Focus Visible (AA) · axe 해당 규칙 없음(수동 측정)
- 영역·종류·확신: 상품 목록, 장바구니 · 포커스 표시 · 확실(측정), 원인은 추정
- 증상 위치: `/#/search`의 `button.btn-basket`, `/#/basket`의 Checkout 버튼
- 원인 위치: `frontend/src/app/product/product.component.scss:116-130`(`.btn-basket`에 `:focus`/`:focus-visible` 규칙 없음) · 추정 · `frontend/src/styles.scss`와 컴포넌트 scss에서 `focus-indicator`, `strong-focus`, `:focus`를 grep했으나 버튼 포커스 스타일은 없음(`styles.scss:21-28`의 `a:focus` 밑줄, `a { outline: none }`만 있음). Material의 `.mat-focus-indicator::before` 테두리는 계산값 `rgba(0, 0, 0, 0)`(투명)이라 남는 표시는 12% 상태 레이어뿐.
- 왜(검증): Tab으로 포커스를 옮긴 뒤 계산 스타일 측정([focus-indicator-measure.txt](./evidence/a11ysweep/focus-indicator-measure.txt)): `outline: none`, 상태 레이어 `opacity 0.12`(`rgb(171,199,255)`). 버튼 배경 `rgb(81,107,119)`가 포커스 시 `rgb(92,118,135)`로 바뀌어 전후 대비 1.18:1. 스크린샷 [focus-add-to-basket.png](./evidence/a11ysweep/focus-add-to-basket.png)에서 첫 번째 Add to Basket이 포커스 상태인데 옆 버튼과 구별이 거의 안 됨. 비교: 상단 바 텍스트 버튼은 같은 0.12 레이어지만 배경이 없던 자리에 알약 모양이 새로 생겨 보임([focus-navbar-account.png](./evidence/a11ysweep/focus-navbar-account.png)), 그래서 여기에 넣지 않음. 상품 카드(`section`)는 브라우저 기본 `outline: auto`가 보임.
- 수정 제안: 전역 스타일에 `@include mat.strong-focus-indicators((border-color: #e8ecef));`를 넣거나 `.btn-basket:focus-visible, .mat-mdc-raised-button:focus-visible { outline: 3px solid #e8ecef; outline-offset: 2px; }` 추가.

### [Medium] About 페이지 고객 의견 캐러셀을 키보드로 넘길 수 없음
- WCAG 기준: 2.1.1 Keyboard (A) · axe `scrollable-region-focusable`, impact serious
- 영역·종류·확신: About · 키보드 · 확실(포커스 가능 요소 0개), 자동 재생 여부는 검증 불가
- 증상 위치: `/#/about`, axe 타깃 `.g-slider`
- 원인 위치: `frontend/src/app/about/about.component.html:42-54`(`<gallery id="feedback-gallery" [autoplay]="true" ...>`) · 추정 · `feedback-gallery`로 grep. 이전/다음 화살표(`i.g-nav-next`)는 ng-gallery 라이브러리가 그리며 `tabIndex -1`. 라이브러리 소스(node_modules)는 사본에 없어 열지 못함.
- 왜(검증): 갤러리 안에서 `tabIndex >= 0`인 요소가 0개. 15초 동안 활성 슬라이드가 0번에서 바뀌지 않음(헤드리스 세션에서 자동 재생이 멈췄을 수 있어 2.2.2 판정은 하지 않음). 키보드 사용자는 첫 번째 의견만 볼 수 있고, 나머지 의견에 키보드로 갈 우회 수단은 확인하지 못함. report-base 규칙 9에 따라 기능 저하(degraded)로 Medium.
- 수정 제안: ng-gallery의 키보드 탐색 옵션을 켜거나, 갤러리 아래에 의견 목록을 일반 텍스트로 둠. 자동 재생을 유지하면 일시정지 버튼 추가.

### [Medium] About 본문 링크가 색으로만 구분되고 주변 글자와 대비 1.31:1
- WCAG 기준: 1.4.1 Use of Color (A) · axe `link-in-text-block`, impact serious
- 영역·종류·확신: About · 색 의존 · 확실
- 증상 위치: `/#/about`, axe 타깃 `a[href$="legal.md"]`
- 원인 위치: `frontend/src/styles.scss:14-18`(`a:link, a:visited { color: tertiary; text-decoration: none; }`), 링크 자체는 `frontend/src/app/about/about.component.html:29` · 확실 · axe가 준 `legal.md`로 grep.
- 왜(검증): 링크 `#70e000`, 주변 문단 `#e3e2e6`(계산값 확인), 대비 1.31:1에 밑줄 없음. 밑줄은 hover/focus 때만 생김(`styles.scss:21-24`). 색을 구별하기 어려운 사용자는 문단 안 링크를 찾기 어려움. 우회 수단은 있음: 링크는 Tab으로 포커스되고 포커스 시 밑줄이 생김. 우회 수단이 있는 장벽이므로 규칙 9에 따라 Medium.
- 수정 제안: 문단 안 링크(`p a`)에 `text-decoration: underline` 상시 적용.

### [Low] 장바구니 제목의 사용자 이메일 대비 1.65:1
- WCAG 기준: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- 영역·종류·확신: 장바구니 · 대비 · 확실
- 증상 위치: `/#/basket`(로그인, 비어 있음/있음 모두), axe 타깃 `small`
- 원인 위치: `frontend/src/app/purchase-basket/purchase-basket.component.scss:19-20` · 확실 · 템플릿 `purchase-basket.component.html:9`의 `<small>{{userEmail}}</small>`에서 scss의 `h1 small`로 추적.
  ```scss
  h1 small {
    color: rgba(0, 0, 0, 0.6);
  ```
- 왜(검증): 어두운 카드 배경 `rgb(62,62,62)` 위 검정 60%. 섞인 글자색 `#191919`, 계산 대비 1.65:1(axe 1.64:1), 25.6px 굵게(큰 텍스트, 기준 3:1). 스크린샷: [basket-heading-contrast.png](./evidence/a11ysweep/basket-heading-contrast.png). 밝은 테마용 값이 어두운 테마에 그대로 남은 것으로 보임. 가려진 정보가 로그인한 본인 이메일이라 Low.
- 수정 제안: `color: var(--theme-text-darker)`(`#b8c0c7`)처럼 테마 변수 사용.

### [Low] 품절 임박 리본("Only 1 left") 대비 부족
- WCAG 기준: 1.4.3 Contrast (Minimum) (AA) · axe `color-contrast`, impact serious
- 영역·종류·확신: 상품 목록 · 대비 · 확실
- 증상 위치: `/#/search`, axe 타깃 `app-product:nth-child(6) > mat-card > article > aside > span[translate=""]`
- 원인 위치: `frontend/src/app/product/product.component.scss:91-100`(`.ribbon { background-color: var(--theme-accent); font: 700 18px/1 ...; text-shadow: 0 1px 1px rgba(0,0,0,0.2) }`), 템플릿 `product.component.html:10-15` · 확실 · `ribbon`으로 grep.
- 왜(검증): 글자 `#e3e2e6`, 리본 배경 `#50a400`, 18px 굵게(13.5pt, 큰 텍스트 기준 14pt 굵게에 못 미쳐 4.5:1 적용). 계산 대비 2.45:1. axe는 text-shadow 색 `#4a9700` 기준으로 2.86:1 보고. 재고 경고를 저시력 사용자가 놓칠 수 있음.
- 수정 제안: 리본 글자를 `#000`으로 하거나 배경을 더 어두운 녹색(`--theme-accent-dark`)으로, 계산 대비 4.5:1 이상 확인.

### [Low] About 캐러셀 이미지에 alt 없음
- WCAG 기준: 1.1.1 Non-text Content (A) · axe `image-alt`, impact critical
- 영역·종류·확신: About · 대체 텍스트 · 확실
- 증상 위치: `/#/about`, axe 타깃 `.g-active-item > gallery-image[imagestate="success"] > .g-image-item[loading="lazy"]`, `gallery-item[galleryindex="1"] > ...`(로드된 2개만 보고. 페이지의 `.g-image-item` 8개 모두 `alt` 없음)
- 원인 위치: `frontend/src/app/about/about.component.ts:124-127` · 확실 · `galleryRef.addImage`로 grep. `{ src, args }`만 넘기고 `alt`가 없음.
- 왜(검증): 이미지는 의견 캡션(`figcaption`) 뒤 배경 사진. 스크린리더가 이름 없는 이미지를 읽거나 파일명을 읽을 수 있음. 캡션 텍스트는 따로 읽히므로 정보 손실은 작음.
- 수정 제안: 배경 사진이므로 `alt: ''`를 넘겨 장식 이미지로 처리.

### [Low] 장바구니 표의 머리글 행에 셀이 없음
- WCAG 기준: 1.3.1 Info and Relationships (A) · axe `aria-required-children`, impact critical
- 영역·종류·확신: 장바구니 · 표 구조 · 확실
- 증상 위치: `/#/basket`(비어 있음/있음 모두), axe 타깃 `mat-header-row`
- 원인 위치: `frontend/src/app/purchase-basket/purchase-basket.component.html:57`(`<mat-header-row>`)과 각 열의 `<mat-header-cell ... class="header-hidden">`(13, 22, 28, 42, 49행), `purchase-basket.component.scss:127-128`(`.header-hidden { display: none; }`) · 확실 · `header-hidden`으로 grep.
- 왜(검증): 머리글 셀이 모두 비어 있고 `display: none`이라 `role="row"`에 자식 셀이 없음. 스크린리더 표 탐색에서 열 이름(상품, 수량, 가격)을 들을 수 없음.
- 수정 제안: 머리글 셀에 열 이름을 넣고 `display: none` 대신 시각적으로만 숨기는 클래스(`cdk-visually-hidden`) 사용.

### [Low] 본문이 랜드마크 밖에 있음(`<main>` 없음)
- 분류: axe best practice `region`, impact moderate · WCAG 기준 없음
- 영역·종류·확신: 앱 셸 · 랜드마크 · 확실
- 증상 위치: 감사한 16개 경로 모두. 대표 타깃 `.search-area`, `h1`, 폼 필드 레이블(`/#/login` 10개, `/#/register` 14개, `/#/photo-wall` 22개 등)
- 원인 위치: `frontend/src/app/app.component.html:15`(`<router-outlet>`이 `<main>` 없이 `mat-sidenav-container` 안에 바로 있음), 검색창 `frontend/src/app/navbar/navbar.component.html:22`(`<div class="search-area">`) · 확실 · axe 타깃 `.search-area`로 grep, 앱 셸 템플릿 확인.
- 왜(검증): 경로마다 best-practice 실행에서 `region` 보고. 스크린리더의 랜드마크 이동으로 본문에 바로 갈 수 없음.
- 수정 제안: `app.component.html`의 `<router-outlet>`을 `<main>`으로 감쌈. 상단 바가 `<nav>`/`header` 랜드마크 안에 있는지 확인.

### [Low] 이미지 alt가 바로 옆 텍스트를 반복
- 분류: axe best practice `image-redundant-alt`, impact minor · WCAG 기준 없음
- 영역·종류·확신: 상단 바 로고, 상품 카드, 장바구니 · 대체 텍스트 · 확실
- 증상 위치: 모든 경로의 `.logo`/`img`(로고), `/#/search`의 `img[alt="Apple Juice (1000ml)"]` 등 상품 이미지 15개
- 원인 위치: `frontend/src/app/navbar/navbar.component.html:17-18`(`alt={{applicationName}}` 다음 줄에 같은 `{{applicationName}}` 텍스트), `frontend/src/app/product/product.component.html:41`, `:46`(`alt="{{ product.name }}"` 뒤에 `{{ product.name }}`) · 확실 · axe 타깃의 `.logo`, `alt=` 로 grep.
- 왜(검증): 스크린리더가 같은 문구를 두 번 읽음.
- 수정 제안: 옆에 같은 텍스트가 있는 이미지는 `alt=""`.

### [Low] 첫 방문 환영 대화상자에 접근 가능한 이름이 없음
- 분류: axe best practice `aria-dialog-name`, impact serious · WCAG 기준 없음
- 영역·종류·확신: 첫 방문 환영 대화상자 · 레이블 · 확실
- 증상 위치: `/#/search` 첫 방문, axe 타깃 `#mat-mdc-dialog-0`
- 원인 위치: `frontend/src/app/welcome/welcome.component.ts:35-41` · 확실 · `dialog.open(WelcomeBannerComponent`로 grep. 옵션이 `minWidth`, `width`, `position`뿐이고 `ariaLabelledBy`/`ariaLabel`이 없음.
- 왜(검증): 대화상자가 열릴 때 스크린리더가 대화상자 제목("Welcome to OWASP Juice Shop!")을 읽지 않음.
- 수정 제안: `ariaLabelledBy`에 배너 `h1`의 id 지정.

### [Low] 지갑 화면 제목 단계가 h1에서 h3로 건너뜀
- 분류: axe best practice `heading-order`, impact moderate · WCAG 기준 없음
- 영역·종류·확신: 지갑 · 제목 구조 · 확실
- 증상 위치: `/#/wallet`, axe 타깃 `.mdc-card[_ngcontent-ng-c4216643156=""] > h3`
- 원인 위치: `frontend/src/app/wallet/wallet.component.html:10`(`<h1>`), `:14`(`<h3>`) · 확실 · `<h3`로 grep.
- 왜(검증): 제목 목록으로 이동하는 스크린리더 사용자에게 h2가 빠진 구조로 보임.
- 수정 제안: 14행을 `<h2>`로.

## 키보드 순회 결과(발견 항목 외)
- `/#/login`([login-tab-order.txt](./evidence/a11ysweep/login-tab-order.txt)): 상단 바 6개 → 이메일 → 비밀번호 → 비밀번호 보기 → "Forgot your password?" → Remember me → "Not yet a customer?" → 문서 끝 → 상단 바로 순환. 순서는 화면 순서와 같고 갇힘 없음. 로그인 버튼은 입력이 비어 있으면 `disabled`라 순서에 없음(값을 넣으면 활성화). 링크는 포커스 시 밑줄이 생김. 접힌 검색 입력(`tabindex="-1"`)은 건너뜀.
- `/#/search`([search-tab-order.txt](./evidence/a11ysweep/search-tab-order.txt)): 상품마다 카드 → Add to Basket 순. 카드에서 Enter → 상세 대화상자가 열리고 포커스가 대화상자 안으로 이동, Escape → 포커스가 카드로 돌아옴. Add to Basket에서 Enter → 담기 동작(이 확인 중 Apple Pomace가 자체 계정 장바구니에 담김).

## 검증 불가
| 항목 | 이유 | 수동 확인 방법 |
|------|------|------|
| `aria-prohibited-attr`: `#searchQuery`(모든 경로), `#rating`·`#captcha`(`/#/contact`) | axe `incomplete`: 역할 없는 요소(`app-mat-search-bar`, `mat-slider`, `code`)의 `aria-label` 지원 여부를 판정하지 못함 | 스크린리더(NVDA/VoiceOver)로 해당 요소에서 이름이 읽히는지 확인 |
| 폼 입력 대비: `/#/login` `#email` `#password`, `/#/register` `#emailControl` `#passwordControl`과 힌트, `/#/forgot-password`, `/#/contact` `#comment` `#captchaControl`, `/#/complain` `#complaintMessage`, `/#/wallet`, `/#/address/create` 7개, `/#/privacy-security/change-password` 3개 | axe `incomplete`: 떠 있는 레이블이 겹쳐 배경색을 정하지 못함 | 입력값을 넣은 상태에서 글자/필드 배경 계산 대비 측정 |
| Add to Basket 버튼 글자 대비(`/#/search`) | axe `incomplete`(가상 요소 배경). 수동 계산은 흰색/`rgb(81,107,119)` 5.65:1이지만 axe 판정이 아니므로 통과로 세지 않음 | 위 수치를 다른 도구로 재확인 |
| `/#/deluxe-membership` 카드 글자 대비 3개 | axe `incomplete`: 배경 그라디언트 | 그라디언트 가장 밝은 지점 기준 측정 |
| `/#/photo-wall` 사진 캡션 대비 | axe `incomplete`: 가상 요소 배경 | 오버레이 표시 상태에서 측정 |
| `/#/basket` 수량 "1" 대비 | axe `incomplete`: 텍스트가 너무 짧음 | 수동 측정 |
| `bypass`(`/#/order-history`, `/#/deluxe-membership`) | axe `incomplete`: 건너뛰기 링크·제목·랜드마크를 찾지 못했지만 판정 보류 | 주문이 있는 상태에서 다시 실행, 건너뛰기 링크 유무 확인 |
| `aria-hidden-focus`(환영 대화상자 열린 상태) | axe `incomplete`: `app-root`가 `aria-hidden="true"`인데 포커스 트랩 앵커가 있음 | 대화상자 열린 상태에서 Tab으로 바깥 요소로 나가는지 확인 |
| About 캐러셀 자동 재생(2.2.2) | 헤드리스 세션에서 15초 동안 슬라이드가 바뀌지 않아 판정 불가 | 일반 브라우저에서 자동 재생과 일시정지 수단 확인 |
| 실제 스크린리더 낭독 | 스크린리더를 돌리지 않음. 이름 관련 판단은 Chrome 접근성 트리 기준 | NVDA/VoiceOver로 상품 목록·장바구니 확인 |
| 키보드 순회(로그인, 상품 목록 외 경로) | 이번 실행은 두 화면만 순회 | `agent-browser press Tab` + 포커스 요소 기록 |
| 로케일 일치, 모바일 뷰포트·탭 타깃 | 승인된 계획에 없음 | 언어 메뉴로 로케일 바꿔 같은 경로 재감사, `set viewport 390 844` |
| 범위 외 29개 경로: `administration`, `accounting`, `address/select`, `address/edit/:addressId`, `delivery-method`, `order-completion/:id`, `order-summary`, `payment/:entity`, `recycle`, `hacking-instructor`, `score-board`, `track-result`, `track-result/new`, `2fa/enter`, `privacy-security`와 하위 `privacy-policy`·`two-factor-authentication`·`data-export`·`last-login-ip`, `juicy-nft`, `wallet-web3`, `web3-sandbox`, `chatbot`과 하위 2개, `bee-haven`, `coding-challenge/:challengeKey`, `403`, `**` | 이번 실행에서 고르지 않음. `score-board`·`privacy-policy`처럼 방문이 챌린지 해결로 기록될 수 있는 경로는 계획(챌린지 고의 해결 금지)에 따라 제외. 관리자/주문 진행 상태가 필요한 경로도 제외 | 경로별로 같은 axe 두 번 실행 |

## 스크린샷·증거 인덱스
- `evidence/a11ysweep/<경로>[-loggedin]-wcag.json`, `-bp.json`: 경로별 axe 원본 결과(axe 4.12.1). 토큰·쿠키 없음.
- `evidence/a11ysweep/search-open-wcag.json`: 검색을 연 상태에서 `#searchQuery` 범위 axe 결과
- `evidence/a11ysweep/home-welcome.png`: 첫 방문, 환영 대화상자와 쿠키 배너
- `evidence/a11ysweep/cookie-banner-contrast.png`: 쿠키 배너(환영 대화상자 닫은 상태)
- `evidence/a11ysweep/basket-heading-contrast.png`: 장바구니 제목 이메일 대비, 수량/삭제 아이콘 버튼
- `evidence/a11ysweep/focus-add-to-basket.png`: 첫 Add to Basket 버튼에 키보드 포커스
- `evidence/a11ysweep/focus-navbar-account.png`: 상단 바 Account 버튼에 키보드 포커스(비교용)
- `evidence/a11ysweep/search-loggedin-snapshot.txt`, `basket-populated-snapshot.txt`: `agent-browser snapshot -i` 접근성 트리
- `evidence/a11ysweep/label-in-name-scan.txt`: 보이는 텍스트와 접근 가능한 이름 비교
- `evidence/a11ysweep/focus-indicator-measure.txt`: Tab마다 포커스 표시 계산값
- `evidence/a11ysweep/login-tab-order.txt`, `search-tab-order.txt`: Tab 순서 기록
