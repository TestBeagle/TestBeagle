# breachsweep 리포트 — OWASP Juice Shop (2026-10-11)

English version: [breachsweep-report-en.md](breachsweep-report-en.md)

## 테스트 범위 및 인가
- 대상: 로컬 실행 중인 OWASP Juice Shop, 컨테이너 `tb-juice`, http://127.0.0.1:3100 (코디네이터가 이미 기동; 본 실행은 기동/중지/재시작하지 않음).
- 인가: 사용자 위임 하에 코디네이터가 본 계획(ladder 1–5, read-only, 127.0.0.1:3100 한정, ≤5 req/s)을 **승인**함. 공개 OSS이며 의도적으로 취약하게 만들어진 교육용 앱이고, 이 머신의 소유자가 로컬에서 직접 구동하며 외부 연동이 없다. 계획 밖 행위는 하지 않았다.
- 방식: 비파괴 read-only. `curl` GET/OPTIONS, 정상 signup API로 내 테스트 계정 A/B 자체 등록, 토큰 보유 상태에서의 교차계정 **읽기**만 수행. 로그인/인증 우회, UNION·데이터 추출, 저장형 페이로드, 내가 만들지 않은 데이터의 쓰기/삭제는 하지 않음.
- 관측 vs 입증 구분: 실제 익스플로잇이 필요한 클래스(SQLi 추출, XSS, 토큰 위조, /ftp 파일 다운로드, 관리자 권한 등록)는 전부 "미검증/범위 외"에 둔다. SOLUTIONS.md·챌린지 힌트 데이터는 근거로 쓰지 않았다.

## 환경
- 소스: image /juice-shop@5658473 · 실행 빌드: bkimminich/juice-shop:latest rev 5658473 (v20.2.0) · 일치: 예 · 빌드 모드: prod
- OS / 런타임: macOS (darwin 27.0.0), Docker 컨테이너 `tb-juice`
- 드라이버: curl (본 실행의 모든 근거는 curl로 수집). agent-browser 0.37.0 사용 가능(세션 변수 준비)했으나 모든 점검이 API/헤더 수준이라 브라우저 탐색이 불필요하여 세션을 열지 않음.
- 시드/데이터: 내가 등록한 계정 A(id 25, basket 6), B(id 26, basket 7). 기존 시드 데이터는 읽기만 함.

## 요약
- 심각도별: Critical 0 · High 4 · Medium 0 · Low 4 · Info 0 (report-base 규칙 9: 민감정보 노출=High, 피해 미입증 설정 관측=Low)
- 입증(demonstrated, read-only 익스플로잇): F1 IDOR, F2 BOLA, F4 JWT 내 비밀번호 해시. 소스 확인: F5 하드코딩 서명키. 관측(observed, 설정·피해 미입증): F3 `/ftp` 리스팅, F6 CSP 부재, F7 와일드카드 CORS, F8 기타 헤더.
- 커버리지: authZ/IDOR · authN · 입력검증(ladder 1–2) · 시크릿 노출 · 헤더/전송 · 클라이언트 번들 점검 수행. 익스플로잇 필요 항목은 미검증.

## 발견 항목

### [HIGH] F1. `/rest/basket/:id` 교차계정 읽기(IDOR)
- 영역·종류·확신: 인가(BOLA/IDOR) · 입증 · 확실
- 증상 위치: `GET /rest/basket/:id`
- 재현: 계정 A(UserId 25, 본인 basket 6) 토큰으로 `GET /rest/basket/7`(B 소유) 요청 → `HTTP 200`, `{"id":7,...,"UserId":26,...}` 반환. 토큰 없이 같은 요청은 `UnauthorizedError`(인증은 강제됨). 근거: [evidence/breachsweep/idor-basket-A-reads-7.txt](evidence/breachsweep/idor-basket-A-reads-7.txt)
- 원인 위치: `server.ts:418` `app.use('/rest/basket/:id', security.isAuthorized())` — 인증만 요구, 소유권 미확인. `routes/basket.ts:19` `BasketModel.findOne({ where: { id } })` 가 경로 파라미터 `id`를 그대로 조회하고, 21–24행의 소유권 비교는 `challengeUtils.solveIf(...)`(챌린지 표시용)일 뿐 접근을 **거부하지 않음**. · 확실(해당 파일 직접 열람)
- 영향: 인증된 임의 사용자가 basket id만 바꿔 타인의 장바구니(상품·쿠폰)를 읽을 수 있음.
- 수정 제안: `retrieveBasket`에서 `req` 토큰의 `bid`와 경로 `id`를 비교해 불일치 시 401/403 반환(현재 `solveIf` 비교 로직을 접근 거부로 승격).

### [HIGH] F2. `/api/Users` 전체 열람·임의 사용자 조회(BOLA)
- 영역·종류·확신: 인가(함수수준 권한) · 입증 · 확실
- 증상 위치: `GET /api/Users`, `GET /api/Users/:id`
- 재현: 일반 customer A 토큰으로 `GET /api/Users` → `HTTP 200`, 전체 26명(admin@juice-sh.op role=admin 포함)의 `email`·`role`·`lastLoginIp` 반환. `GET /api/Users/1` → 관리자 레코드 반환. 토큰 없이는 `UnauthorizedError`. 근거: [evidence/breachsweep/authz-A-lists-all-users.txt](evidence/breachsweep/authz-A-lists-all-users.txt), [evidence/breachsweep/authz-A-reads-user1.txt](evidence/breachsweep/authz-A-reads-user1.txt)
- 원인 위치: `server.ts:382` `app.get('/api/Users', security.isAuthorized())` 와 `server.ts:383-384` `app.route('/api/Users/:id').get(security.isAuthorized())` — 인증만 걸고 역할/소유권 제한 없음. 이후 `server.ts:500` `finale.initialize(...)`가 User 모델 전체를 자동 서빙. (PUT/DELETE는 `denyAll()`로 막혀 있으나 GET은 열려 있음.) · 확실(직접 열람). 참고: 응답에는 `password`/`totpSecret`이 빠져 있어 그 필드 유출은 이 경로에서는 없음.
- 영향: 인증된 임의 customer가 전체 사용자 명부(이메일·역할·마지막 접속 IP)를 열람. 사용자 열거·표적화 가능.
- 수정 제안: `GET /api/Users`·`/api/Users/:id`에 역할 검사(관리자 전용) 또는 본인 레코드 한정 필터 추가. finale 자동 노출을 명시적 핸들러로 대체.

### [LOW] F3. `/ftp` 디렉터리 리스팅이 인증 없이 노출(관측)
- 영역·종류·확신: 파일 노출 · 관측 · 확실(관측된 응답)
- 증상 위치: `GET /ftp`(런타임 확인). `/encryptionkeys`, `/support/logs`, `/.well-known`, `/infrastructure`는 소스에서만 확인 — 런타임 증거 미저장이고 컨테이너 중지로 재확인 불가 → 런타임 미검증.
- 재현: `GET /ftp` → 디렉터리 목록 HTML. `ftp/coupons_2013.md.bak`, `ftp/package.json.bak`, `ftp/package-lock.json.bak`, `ftp/incident-support.kdbx`(KeePass DB), `ftp/announcement_encrypted.md`, `ftp/encrypt.pyc`, `ftp/suspicious_errors.yml` 등 **파일명**이 링크로 노출(내용은 열람하지 않음). 근거: [evidence/breachsweep/ftp-listing.txt](evidence/breachsweep/ftp-listing.txt)
- 원인 위치: `server.ts:288` `serveIndex('ftp', ...)`(런타임+소스 확실). 같은 패턴이 소스에 있는 `server.ts:296` `/encryptionkeys`, `server.ts:300` `/support/logs`, `server.ts:292` `/.well-known`, `server.ts:268` `/infrastructure`는 설정만 확실하고 런타임 미검증. · `/ftp` 확실, 나머지 설정만 확실
- 영향: 백업·자격증명 컨테이너로 보이는 **파일명**이 비인증으로 드러남. 내용은 열람하지 않아 피해 미입증 → Low. 파일 내용 다운로드·확장자 필터 우회가 성공하면 민감정보 노출(High)이 되나 그것은 미검증.
- 수정 제안: 운영 환경에서 `serveIndex` 디렉터리 브라우징 제거, `/ftp`·`/encryptionkeys`를 인증·인가 뒤로 이동하거나 노출 자체 제거.

### [HIGH] F4. JWT 페이로드에 비밀번호 해시 포함(입증)
- 영역·종류·확신: 민감정보 노출 · 입증 · 확실
- 증상 위치: `POST /rest/user/login` 이 발급하는 JWT 본문
- 재현: 내 계정 A 토큰의 payload(base64, 비암호화)를 디코드하니 `data` 키에 `password`(비어 있지 않은 hex 문자열 — 앱은 무염 MD5로 저장, `lib/insecurity.ts:41`)와 `totpSecret` 키가 포함. `totpSecret`은 키만 있고 값은 비어 있다: `routes/login.ts:37-48`에 따라 이 로그인 토큰은 `totpSecret === ''`인 사용자에게만 발급되고, 2FA 사용자는 401 `tmpToken`을 받는다(채워진 2FA 시드가 토큰에 들어가는지는 검증 불가 표 참조). 반면 `GET /api/Users/:id`는 두 필드를 제외함 → 비밀번호 해시 노출은 토큰 본문 특유. 근거: [evidence/breachsweep/jwt-embeds-sensitive-fields.txt](evidence/breachsweep/jwt-embeds-sensitive-fields.txt) (토큰 값은 `<redacted>`)
- 원인 위치: `routes/login.ts:23-24` `{ data: user, bid }` 를 `security.authorize(authenticatedUser)`에 그대로 전달. `lib/insecurity.ts:54` `jwt.sign(user, privateKey, ...)` — 받은 객체를 그대로 서명(민감 필드 제거 없음). · 확실(직접 열람)
- 영향: 비암호화 base64 토큰을 손에 넣은 누구나 비밀번호 MD5 해시(무염 → 크래킹 대상)를 읽음. report-base 규칙 9의 "민감정보 노출" → High.
- 수정 제안: 토큰에 넣을 필드를 `{ id, email, role }` 등 최소 집합으로 화이트리스트. `authorize()` 입력에서 `password`·`totpSecret` 제거.

### [HIGH] F5. 서명/암호 비밀키가 소스에 하드코딩(소스 확인)
- 영역·종류·확신: 시크릿 노출 · 소스 확인 · 확실(소스 열람). 규칙 9: 서명 비밀키(민감정보) 노출 → High.
- 증상 위치: JWT 서명키/HMAC 키
- 재현: `lib/insecurity.ts:21` 에 RSA private key 문자열 상수, `lib/insecurity.ts:42` 에 HMAC 키 `<redacted>` 하드코딩. 매칭되는 공개키 파일은 소스상 serve-index 대상 경로(`encryptionkeys/jwt.pub`, F3)에 존재 — 런타임 노출 여부는 미검증.
- 원인 위치: `lib/insecurity.ts:21`, `lib/insecurity.ts:42` · 확실(직접 열람)
- 영향: 서명키가 공개 소스에 고정 상수로 존재. **이 키로 토큰을 위조해 권한 상승하는 것은 실제 익스플로잇이므로 미검증/범위 외**.
- 수정 제안: 키를 소스에서 분리해 환경변수/시크릿 매니저로 주입, 배포별 키 회전.

### [LOW] F6. Content-Security-Policy 헤더 없음(관측)
- 영역·종류·확신: 보안 헤더 누락 · 관측 · 확실. 규칙 9: 설정 관측이며 XSS 등 실제 피해 미입증 → Low(모범사례).
- 증상 위치: 모든 응답 헤더
- 재현: `GET /` 응답에 `Content-Security-Policy` 부재. 근거: [evidence/breachsweep/headers-root.txt](evidence/breachsweep/headers-root.txt)
- 원인 위치: `server.ts:186-188` — `helmet.noSniff()`·`helmet.frameguard()`만 적용하고 `helmet.contentSecurityPolicy()` 미적용. `server.ts:188`에서 `helmet.xssFilter()`가 주석 처리됨. · 확실(직접 열람)
- 영향: XSS 발생 시 스크립트 출처 제한·인라인 차단 등 완화 장치 부재.
- 수정 제안: 최소 `default-src 'self'`부터 CSP 도입, 스크립트/스타일 출처 화이트리스트 정의.

### [LOW] F7. 과도하게 허용적인 CORS(`Access-Control-Allow-Origin: *`)(관측)
- 영역·종류·확신: CORS 설정 · 관측 · 확실. 규칙 9: 설정 관측이며 Bearer 토큰 인증이라 데이터 탈취 미입증 → Low.
- 증상 위치: 모든 응답, 프리플라이트 포함
- 재현: `GET /` 및 `Origin: https://evil.example` 로 보낸 `OPTIONS /rest/products/search` 모두 `Access-Control-Allow-Origin: *` 반환(204). 근거: [evidence/breachsweep/cors-preflight.txt](evidence/breachsweep/cors-preflight.txt)
- 원인 위치: `server.ts:182-183` `app.options('*', cors())` / `app.use(cors())` — 오리진 제한 없는 무제한 적용. · 확실(직접 열람)
- 영향: 임의 오리진이 응답을 읽을 수 있음. 단 인증이 쿠키가 아닌 Bearer 토큰이라 와일드카드 CORS 단독으로 즉시 자격증명 탈취는 아님(그 입증은 범위 밖). API 응답 노출 표면이 넓어짐.
- 수정 제안: 허용 오리진을 명시적 화이트리스트로 제한.

### [LOW] F8. 기타 헤더: HSTS·Referrer-Policy 부재, 내부 경로 노출(관측)
- 영역·종류·확신: 보안 헤더/정보 노출 · 관측 · 확실
- 증상 위치: 모든 응답 헤더
- 재현: 응답에 `Strict-Transport-Security`·`Referrer-Policy` 부재, `X-Recruiting: /#/jobs` 존재. 근거: [evidence/breachsweep/headers-root.txt](evidence/breachsweep/headers-root.txt)
- 원인 위치: `server.ts:186-188`(helmet 기본값 미적용), `server.ts:198` `res.append('X-Recruiting', ...)` · 확실(직접 열람)
- 영향: HSTS는 **로컬 HTTP 환경에서는 프로덕션 영향을 입증할 수 없음**(배포 시 HTTPS에서만 의미). Referrer-Policy 부재 시 외부 이동에 전체 URL이 Referer로 유출 가능. `X-Recruiting`는 경미한 불필요 정보.
- 수정 제안: TLS 종단에서 `Strict-Transport-Security` 설정, `Referrer-Policy: strict-origin-when-cross-origin`, 운영 응답에서 `X-Recruiting` 제거.

## 관측했으나 발견으로 올리지 않은 것(정상/판단 보류)
- `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` 존재(`server.ts:186-187`). 정상.
- `/api/Users` 는 토큰 없이는 `UnauthorizedError` — 인증 자체는 강제됨(문제는 인가, F2).
- `/rest/products/search?q='`(단일 따옴표) → `HTTP 200` `{"status":"success","data":[]}`, SQL 오류 누출 없음. (SQLi 입증은 조작 페이로드 필요 → 범위 밖.)
- `GET /main.js.map` 은 `HTTP 200`이나 내용이 SPA `index.html`(text/html, 9393B; 존재하지 않는 `/nope.js.map`도 동일). **소스맵 노출 아님** — 거짓양성으로 제외.

## 검증 불가 / 범위 외
| 항목 | 이유 | 인가된 환경에서의 확인 방법 |
|------|------|------|
| SQL 인젝션(로그인 우회·검색 추출) | 로그인 우회·UNION/추출 계획상 금지; 단일 따옴표로는 오류 미누출 | 재시드 가능한 스테이징에서 조작 페이로드로 입력검증 테스트 |
| XSS(반사/저장) | 저장형 페이로드·스크립트 주입 미실행 | 검색·리뷰 입력에 inert 마커 후 반영/실행 관찰 |
| JWT 위조·권한 상승 | 토큰 조작·인증 우회 범위 밖 | 하드코딩 키(F5)로 토큰 서명/검증 테스트 |
| 채워진 TOTP 시드의 토큰 노출 | `routes/login.ts:37-48`상 2FA 사용자는 로그인 토큰 대신 401 tmpToken을 받아, 2FA 활성 계정 토큰을 확보 못 함 | 2FA 활성 계정으로 전체 로그인 완료 후 발급 토큰 payload 디코드 |
| `/ftp` 파일 다운로드·확장자 필터 우회 | 추출 범위 밖 | `curl /ftp/<file>.bak`, Poison Null Byte 등 |
| 관리자 역할로 회원가입(권한 상승) | 권한 상승 익스플로잇 범위 밖 | signup에 `role` 전달 후 승격 여부 확인 |
| 레이트리밋·브루트포스 | 대량 요청 금지(≤5 req/s) | 인가된 부하 환경에서 별도 측정 |
| 의존성 취약점(`npm audit`) | SRC의 node_modules 제거됨 + 오프라인·다운로드 금지로 캐시 없음 | 네트워크 허용 환경에서 `npm audit` 실행 |

## 증거 인덱스
`docs/examples/juice-shop/evidence/breachsweep/` (토큰/JWT/쿠키/비밀번호는 `<redacted>`):
- `headers-root.txt` — 루트 응답 헤더(F6/F7/F8)
- `idor-basket-A-reads-7.txt` — F1 교차계정 basket 읽기
- `authz-A-lists-all-users.txt`, `authz-A-reads-user1.txt` — F2 사용자 열람
- `jwt-embeds-sensitive-fields.txt` — F4 토큰 내 민감필드
- `cors-preflight.txt` — F7 프리플라이트
- `ftp-listing.txt` — F3 디렉터리 리스팅
- `register-a.json`/`register-b.json`, `login-a.json`/`login-b.json`(토큰 redacted), `accounts.txt` — 계정 A/B 셋업
- `sqli-errorleak-search-quote.txt` — 단일 따옴표 관측(오류 미누출)

bugsweep·a11ysweep는 같은 앱에서 병렬 수행되며 그 쪽 이슈는 중복 기재하지 않음.
