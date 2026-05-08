# Dependency Contract: {프로젝트명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: 모든 BUILD 에이전트
> 상태: draft | active | deprecated

---

## 핵심 규칙

- 버전은 **정확한 핀**. `^`, `~`, `>=` 등 범위 표기 금지.
- 에이전트가 이 계약서에 없는 라이브러리를 임의 추가 ❌
- 새 라이브러리 필요 시 → 오케스트레이터 보고 → 계약서 update → 코드 변경
- 잠금 파일(`package-lock.json` / `requirements.txt` / `pubspec.lock`)은 항상 이 계약과 정합

---

## 런타임 버전

| 런타임 | 버전 |
|--------|------|
| node | 20.11.1 |
| python | 3.11.7 |
| dart | 3.3.0 |

---

## 핵심 의존성

### Backend (예: Python)

| 패키지 | 버전 | 비고 |
|--------|------|------|
| fastapi | 0.111.0 | |
| sqlalchemy | 2.0.30 | |
| pydantic | 2.7.1 | |
| `passlib[bcrypt]` | 1.7.4 | bcrypt는 passlib을 통해서만 |
| bcrypt | 4.0.1 | passlib 1.7.4와 호환되는 버전 |
| psycopg2-binary | 2.9.9 | |

### Frontend (예: TypeScript)

| 패키지 | 버전 | 비고 |
|--------|------|------|
| next | 14.2.3 | |
| react | 18.3.1 | |
| react-dom | 18.3.1 | |
| zod | 3.23.8 | |

---

## 호환성 주의사항

알려진 문제:

- **bcrypt 4.1+ 와 passlib 1.7.4 비호환** → bcrypt는 4.0.x 이하만 사용
- **prisma + ts-node** 조합은 `--esm` 플래그 필요
- **react 19** 일부 라이브러리 미지원 → 18.x 유지

---

## 잠금 파일 위치

| 잠금 파일 | 경로 |
|----------|------|
| Python | `requirements.txt` (루트) |
| Node | `package-lock.json` (루트) |
| Flutter | `pubspec.lock` (루트) |

VERIFY Tier 0이 이 파일을 계약서와 비교한다.

---

## 환경변수 (Constants Contract와 cross-reference)

| 키 | 출처 |
|----|------|
| `DB_HOST` | `docker-compose.yml` POSTGRES_HOST |
| `DB_PORT` | `docker-compose.yml` POSTGRES_PORT |
| `DB_NAME` | `docker-compose.yml` POSTGRES_DB |
| `DB_USER` | `docker-compose.yml` POSTGRES_USER |
| `DB_PASSWORD` | `docker-compose.yml` POSTGRES_PASSWORD |

`config.py` 같은 코드 파일은 `os.getenv()`로만 읽고 값을 직접 정의 ❌

---

## Lint 통과 의무

`references/contract-lint.md`의 Dependency 체크리스트:
- 모든 핵심 라이브러리가 정확한 핀
- 런타임 버전 명시
- 잠금 파일 위치 명시
- peer dep 충돌 가능성 검증

`pip check` / `npm ls` / `flutter pub deps` 결과 첨부 권장.
