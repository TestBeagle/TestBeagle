# breachsweep 리포트 — OWASP Juice Shop (2026-09-08)

## 테스트 범위 및 인가
- 대상: 로컬 실행한 OWASP Juice Shop 20.2.0(`docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop`). 공개 OSS이며 의도적으로 취약하게 만들어진 교육용 앱이라 공개 테스트에 문제 없음.
- 방식: **비파괴, read-only**. `curl` GET과 정적 헤더/응답 관찰만 수행. 주입·인젝션·데이터 변경·삭제·대량 요청·인증 우회 시도는 하지 않음.
- 중요한 프레이밍: Juice Shop은 SQLi·XSS·IDOR 등이 **의도적으로** 심어진 앱이다. 이 리포트는 그 취약점들을 "찾았다"고 주장하지 않는다. 비파괴 GET만으로 근거가 남는 **설정 수준 노출**만 발견으로 올리고, 실제 공격이 필요한 취약점 클래스는 전부 "미검증/범위 외"에 둔다. 이것이 breachsweep의 원칙이다.

## 요약
- 심각도별: High 1 · Medium 3 · Low 2 · Info 0
- 근거: 전부 `curl` GET 응답(헤더·본문)으로 재현 가능. 확신은 모두 "확실"(관측된 응답 그대로).

## 발견 항목

### [HIGH] `/ftp` 디렉터리 리스팅이 인증 없이 노출
- 유형 · 위치 · 확신: 민감 파일 노출 · `GET /ftp` · 확실
- 재현: `curl -s http://localhost:3000/ftp` → 디렉터리 목록 HTML 반환. `ftp/coupons_2013.md.bak`, `ftp/package.json.bak`, `ftp/package-lock.json.bak`, `ftp/incident-support.kdbx`(KeePass DB), `ftp/announcement_encrypted.md`, `ftp/encrypt.pyc`, `ftp/eastere.gg` 등이 링크로 노출.
- 영향: 백업 파일·자격증명 컨테이너로 보이는 파일 목록이 그대로 드러남. 실제 다운로드 가능 여부·확장자 필터는 이 비파괴 관찰 범위 밖(아래 미검증).
- 수정 제안: 정적 파일 서빙 경로에서 디렉터리 리스팅 비활성화, `/ftp`를 인증·인가 뒤로 이동하거나 노출 제거.

### [MEDIUM] Content-Security-Policy 헤더 없음
- 유형 · 위치 · 확신: 보안 헤더 누락 · 모든 응답 · 확실
- 재현: `curl -s -D - http://localhost:3000/` 응답 헤더에 `Content-Security-Policy` 부재. axe-core를 외부 CDN(`cdnjs.cloudflare.com`)에서 페이지에 주입해 실행하는 것이 실제로 성공했고(a11ysweep 실행 로그), 이는 스크립트 출처 제한이 없음을 방증.
- 영향: XSS 발생 시 완화 장치 부재. 임의 외부 스크립트 로드·인라인 실행이 차단되지 않음.
- 수정 제안: 최소 `default-src 'self'`부터 시작하는 CSP 도입, 인라인/외부 스크립트 화이트리스트 정의.

### [MEDIUM] 과도하게 허용적인 CORS (`Access-Control-Allow-Origin: *`)
- 유형 · 위치 · 확신: CORS 설정 · 모든 응답 · 확실
- 재현: `GET /` 응답 헤더 `Access-Control-Allow-Origin: *`. 서버 코드에서도 `app.use(cors())`를 무제한으로 적용(`server.ts`).
- 영향: 임의 오리진이 응답을 읽을 수 있음. 인증이 쿠키가 아닌 토큰이면 즉시 자격증명 유출은 아니나, API 응답 노출 표면이 넓어짐.
- 수정 제안: 허용 오리진을 명시적 화이트리스트로 제한.

### [MEDIUM] HSTS(`Strict-Transport-Security`) 헤더 없음
- 유형 · 위치 · 확신: 보안 헤더 누락 · 모든 응답 · 확실
- 재현: 응답 헤더에 `Strict-Transport-Security` 부재.
- 영향: HTTPS 강제 부재로 다운그레이드/중간자 위험. (로컬은 HTTP지만 프로덕션 배포 시 그대로면 문제.)
- 수정 제안: TLS 종단에서 `Strict-Transport-Security: max-age=31536000; includeSubDomains` 설정.

### [LOW] `Referrer-Policy` 헤더 없음
- 유형 · 위치 · 확신: 보안 헤더 누락 · 모든 응답 · 확실
- 재현: 응답 헤더에 `Referrer-Policy` 부재.
- 영향: 외부 이동 시 전체 URL이 Referer로 유출될 수 있음.
- 수정 제안: `Referrer-Policy: strict-origin-when-cross-origin` 설정.

### [LOW] `X-Recruiting` 커스텀 헤더로 내부 경로 노출
- 유형 · 위치 · 확신: 정보 노출 · 모든 응답 · 확실
- 재현: `GET /` 헤더 `X-Recruiting: /#/jobs`.
- 영향: 경미하나 불필요한 정보. 표면 축소 관점에서 제거 권장.
- 수정 제안: 프로덕션 응답에서 제거.

## 관측했으나 발견으로 올리지 않은 것(정상/판단 보류)
- `helmet.noSniff()`·`helmet.frameguard()` 적용 확인: 응답에 `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` 존재(확실). 정상.
- 오류 응답 스택 노출: `GET /rest/products/<invalid>/reviews`, `GET /rest/track-order/%27` 모두 정상 형태 JSON(`{"status":"success",...}`) 반환, 스택 트레이스 유출 없음(확실). 이 엔드포인트들에 한해 정상.
- `/.well-known/security.txt`: `200`. 존재.

## 미검증 / 범위 외 (비파괴 원칙상 실행하지 않음 — "정상"이 아님)
| 항목 | 이유 | 확인 방법(인가된 환경에서) |
|------|------|------|
| SQL 인젝션(로그인 우회 등) | 페이로드 주입은 파괴적 가능성 → 미실행 | 인가된 스테이징에서 `' OR 1=1--` 류로 로그인 폼 테스트 |
| XSS(반사/저장) | 스크립트 주입 미실행 | 검색·리뷰 입력에 `<script>` 페이로드 후 실행 여부 관찰 |
| IDOR / 접근제어(`/api/Users`, basket, order) | 타 사용자 리소스 접근 시도 미실행 | 인가된 계정 두 개로 상호 리소스 ID 접근 비교 |
| `/ftp` 파일 실제 다운로드·확장자 필터 우회 | 다운로드·우회는 범위 밖 | `curl /ftp/<file>.bak`, Poison Null Byte 등 |
| JWT 위·변조, 관리자 권한 상승 | 토큰 조작 미실행 | 토큰 alg/서명 검증 테스트 |
| 자동화 봇 방어·레이트리밋 | 대량 요청 금지 원칙 | 인가된 부하 환경에서 별도 측정 |

## 스크린샷·증거
헤더·엔드포인트 근거는 위 재현 커맨드로 즉시 재현 가능. 화면 근거는 bugsweep 리포트의 `screenshots/` 참조.
