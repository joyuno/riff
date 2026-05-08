# Security Contract: {모듈명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: {에이전트명}
> 상태: draft | active | deprecated

---

## 개요

{이 계약서가 다루는 기능의 보안 경계 설명}

---

## 인증 요구사항

| 엔드포인트 | 인증 필요 | 인증 방법 | 비고 |
|-----------|----------|----------|------|
| `GET /api/public/*` | 불필요 | — | 공개 API |
| `GET /api/example` | 필요 | Bearer JWT | 본인 데이터만 |
| `POST /api/example` | 필요 | Bearer JWT | — |
| `DELETE /api/admin/*` | 필요 | Bearer JWT + MFA | 관리자 전용 |
| `GET /api/health` | 불필요 | — | 헬스체크 |

### JWT 토큰 규격

```
- 알고리즘: RS256 (HS256 금지)
- Access Token 만료: 15분
- Refresh Token 만료: 7일
- 발급자(iss): "https://auth.example.com"
- 대상(aud): "https://api.example.com"
- 필수 클레임: sub, iat, exp, iss, aud, role
```

---

## 역할 기반 권한 매트릭스

| 리소스 | 작업 | GUEST | USER | MODERATOR | ADMIN |
|--------|------|-------|------|-----------|-------|
| 공개 게시물 | 읽기 | O | O | O | O |
| 본인 게시물 | 생성/수정/삭제 | X | O | O | O |
| 타인 게시물 | 수정 | X | X | O | O |
| 타인 게시물 | 삭제 | X | X | O | O |
| 사용자 목록 | 읽기 | X | X | O | O |
| 사용자 권한 | 변경 | X | X | X | O |
| 시스템 설정 | 읽기/변경 | X | X | X | O |

**원칙**: 최소 권한 원칙 적용. 명시되지 않은 것은 기본적으로 거부.

---

## 입력 검증 규칙

### 공통 규칙

| 필드 유형 | 최대 길이 | 허용 형식 | 금지 패턴 |
|----------|----------|---------|---------|
| 이름 | 100자 | 문자, 숫자, 공백 | SQL 예약어, HTML 태그 |
| 이메일 | 254자 | RFC 5321 표준 | — |
| 비밀번호 | 128자 | 최소 8자, 대소문자+숫자+특수문자 | — |
| URL | 2048자 | HTTP/HTTPS만 허용 | javascript: 스킴, data: 스킴 |
| 자유 텍스트 | 5000자 | HTML 이스케이프 필수 | script 태그, 인라인 이벤트 핸들러 |
| 파일명 | 255자 | 영문, 숫자, -, _ | 경로 탐색 문자, null byte |

### 모듈별 추가 규칙

```
{모듈명} 전용 검증:
- {필드명}: {규칙}
- {필드명}: {규칙}
```

---

## CORS 정책

```
허용 출처 (Origin):
  - 프로덕션: https://example.com, https://www.example.com
  - 스테이징: https://staging.example.com
  - 개발: http://localhost:3000 (개발 환경만)

허용 메서드: GET, POST, PUT, PATCH, DELETE, OPTIONS

허용 헤더: Content-Type, Authorization, X-Request-ID

노출 헤더: X-RateLimit-Limit, X-RateLimit-Remaining, X-Request-ID

자격증명(credentials): true

프리플라이트 캐시: 86400초 (24시간)
```

---

## 비밀 정보 처리 규칙

### 로그에 절대 포함하면 안 되는 필드

```
- password (모든 형태: password, passwd, pwd, newPassword)
- token (accessToken, refreshToken, apiToken)
- secret (clientSecret, apiSecret)
- creditCard, cardNumber, cvv, expiryDate
- ssn, socialSecurityNumber
- 개인식별번호, 주민등록번호
```

### 응답에 절대 포함하면 안 되는 필드

```
- 비밀번호 해시
- 내부 시스템 경로
- 스택 트레이스 (프로덕션)
- 다른 사용자의 개인정보
- 내부 에러 메시지 원문 (일반화하여 반환)
```

### 환경변수 관리

```
- DB 비밀번호, API 키는 환경변수로만 관리
- 코드, 주석, 로그에 직접 작성 금지
- .env 파일은 .gitignore에 포함
- 프로덕션: 비밀 관리 서비스 사용 (AWS Secrets Manager 등)
```

---

## 속도 제한 (Rate Limiting)

| 대상 | 제한 | 기준 | 초과 응답 |
|------|------|------|---------|
| 인증되지 않은 요청 | 60회/분 | IP | 429 |
| 인증된 요청 | 1000회/분 | 사용자 ID | 429 |
| 로그인 시도 | 5회/분 | IP + 이메일 | 429 + 잠금 |
| 파일 업로드 | 10회/시간 | 사용자 ID | 429 |
| 비밀번호 재설정 | 3회/시간 | 이메일 | 429 |

---

## SQL 인젝션 방지

- ORM/쿼리 빌더의 파라미터 바인딩만 사용
- 동적 SQL 문자열 조합 금지
- 사용자 입력을 쿼리에 직접 삽입 금지

## XSS 방지

- 모든 사용자 입력: HTML 이스케이프 후 저장 또는 출력
- Content Security Policy (CSP) 헤더 설정 필수
- 사용자 데이터를 DOM에 동적으로 삽입할 때 textContent 사용 (innerHTML 직접 조작 금지)
- JSON.parse()를 이용한 안전한 데이터 파싱 (임의 코드 실행 방지)

## CSRF 방지

- 상태 변경 요청 (POST/PUT/DELETE): CSRF 토큰 검증
- SameSite=Strict 쿠키 설정
- Origin 헤더 검증

---

## 보안 헤더

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self'; ...
```

---

## 변경 이력

| 날짜 | 변경 내용 | 변경자 |
|------|-----------|--------|
| {YYYY-MM-DD} | 최초 생성 | {에이전트명} |
