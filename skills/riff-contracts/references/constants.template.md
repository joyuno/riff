# Constants Contract: {모듈명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: {프론트, 백엔드 등}
> 상태: draft | active | deprecated

---

## 핵심 규칙

이 계약서에 정의된 값은 **다른 파일에서 다시 하드코딩 금지**.
반드시 이 계약서에서 import 또는 환경변수로 읽어 사용.

값을 변경할 때 → 코드를 먼저 바꾸지 말고 이 계약서를 먼저 update → 코드는 거기에 맞춤.

---

## 검증 상수 (입력 길이/형식)

| 키 | 값 | 단위 | 의미 |
|----|----|------|------|
| `PASSWORD_MIN_LENGTH` | 8 | 문자 (포함) | 비밀번호 최소 길이 |
| `PASSWORD_MAX_LENGTH` | 128 | 문자 (포함) | 비밀번호 최대 길이 |
| `EMAIL_MAX_LENGTH` | 254 | 문자 (포함) | 이메일 최대 길이 (RFC 5321) |
| `USERNAME_REGEX` | `^[a-z0-9_]{3,20}$` | — | 영소문자 숫자 underscore, 3~20자 |

---

## Rate Limit

| 키 | 값 | 단위 | 의미 |
|----|----|------|------|
| `SIGNUP_RATE_LIMIT` | 5 | 회/IP/분 | 가입 시도 |
| `LOGIN_RATE_LIMIT` | 10 | 회/IP/분 | 로그인 시도 |
| `RATE_LIMIT_STATUS` | 429 | HTTP code | 초과 시 응답 |

---

## 토큰 정책 (Security Contract와 cross-reference)

| 키 | 값 | 단위 |
|----|----|------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | 분 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | 일 |

---

## 페이지네이션

| 키 | 값 | 단위 |
|----|----|------|
| `DEFAULT_PAGE_SIZE` | 20 | 항목 |
| `MAX_PAGE_SIZE` | 100 | 항목 |
| `FIRST_PAGE_NUMBER` | 1 | 페이지 |

---

## 에러 코드 매핑

| 코드 | HTTP | 메시지 |
|------|------|------|
| `VALIDATION_ERROR` | 400 | 입력값이 올바르지 않습니다 |
| `UNAUTHORIZED` | 401 | 인증이 필요합니다 |
| `FORBIDDEN` | 403 | 권한이 없습니다 |
| `NOT_FOUND` | 404 | 리소스를 찾을 수 없습니다 |
| `CONFLICT` | 409 | 중복된 리소스 |
| `INTERNAL_ERROR` | 500 | 서버 오류 |

---

## 환경변수 (출처 명시)

| 키 | 출처 (SSOT) | 비고 |
|----|------------|------|
| `DATABASE_URL` | `.env` | 직접 정의 |
| `POSTGRES_HOST` | `docker-compose.yml` environment | 컨테이너 호스트 |
| `JWT_SECRET` | `.env`, 절대 git 커밋 ❌ | 암호화 키 |

---

## Lint 통과 의무

이 계약서는 `references/contract-lint.md`의 Constants 체크리스트를 통과해야 한다.
특히:
- 모든 수치에 단위 명시
- bound 포함/미포함 명시
- SSOT 위반(같은 키 두 번 정의) 없음
