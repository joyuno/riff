# 스택별 에러 패턴 및 탐지 명령

이 파일은 Constants Contract·Dependency Contract 작성 시,
그리고 Tier 0 스캔 실행 시에만 읽는다.
SKILL.md에 포함하지 않는다.

---

## Constants — 스택별 불일치 에러 패턴

| 스택 조합 | 불일치 시 증상 |
|----------|--------------|
| Python/FastAPI+Pydantic ↔ React | 백엔드: HTTP 422 `{"detail":[{"type":"string_too_short"}]}` / 프론트: 제출 성공 후 서버 에러 |
| Python/FastAPI+Pydantic ↔ Flutter | 백엔드: 422 / Flutter: statusCode 422 파싱 실패 또는 조용히 무시 |
| Node/Zod or Joi ↔ React | 백엔드: HTTP 400 + 에러 JSON / 프론트: 400 에러 |
| Node/Zod or Joi ↔ Flutter | 백엔드: 400 / Flutter: Exception 또는 조용한 실패 |
| Flutter 내부 (위젯↔서비스) | Dart assertion error, StateError, 또는 에러 없이 다른 결과 |
| Go ↔ React/Flutter | 백엔드: 400 `{"error":"Key: 'Field' Error:..."}` |

## Constants — 스택별 탐지 명령

```bash
# Python/FastAPI + Pydantic
grep -rn "min_length\|max_length\|ge=\|le=" backend/ --include="*.py"

# Node.js + Zod/Joi
grep -rn "\.min(\|\.max(" src/ --include="*.ts" --include="*.js"

# React 프론트엔드
grep -rn "minLength\|maxLength\|min:\|max:" src/ --include="*.tsx" --include="*.jsx"

# Flutter
grep -rn "length\|validator" lib/ --include="*.dart"

# Go
grep -rn 'binding:"min=\|binding:"max=' . --include="*.go"
```

---

## Dependency — 스택별 충돌 에러 패턴

| 스택 | 충돌 유형 | 에러 패턴 |
|------|-----------|-----------|
| Python | 라이브러리 비호환 | `ImportError`, `AttributeError: module 'bcrypt' has no attribute '...'` |
| Python | config↔docker 불일치 | `OperationalError: FATAL: password authentication failed` |
| Python | ORM↔SQL 스키마 불일치 | `ProgrammingError: column "X" does not exist` |
| Node.js | 패키지 버전 충돌 | npm `ERESOLVE`, `peer dep conflict`, `Cannot find module` |
| Node.js | Prisma↔DB 스키마 불일치 | `PrismaClientKnownRequestError: Unknown field 'X'` |
| Flutter/Dart | pub 버전 충돌 | `version solving failed` |
| Flutter/Dart | 패키지 API 변경 | `The method 'X' isn't defined` (Dart 컴파일 에러) |
| Go | 모듈 불일치 | `ambiguous import`, `go: finding module for package X` |

## Dependency — 스택별 사전 검증 명령

```bash
# Python
pip check

# Python: docker ↔ config 키 비교
diff <(grep -oP 'POSTGRES_\w+' docker-compose.yml | sort -u) \
     <(grep -oP 'POSTGRES_\w+' config.py | sort -u)

# Python: ORM ↔ SQL 컬럼 비교
grep -n "Column\|mapped_column" models.py
grep -n "CREATE TABLE\|ADD COLUMN" init.sql

# Node.js
npm ls 2>&1 | grep -i "WARN\|ERR"

# Flutter
flutter pub deps 2>&1 | grep -i "conflict\|incompatible"

# Go
go mod verify
```
