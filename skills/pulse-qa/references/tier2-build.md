# Tier 2: 빌드/타입 QA — 상세 가이드

Tier 1 경계면 분석을 통과한 뒤 실행한다.
정적 도구로 잡을 수 있는 타입 에러, 린트 위반, 번들 실패를 전부 제거한다.

---

## 실행 순서

```bash
# 1단계: TypeScript 타입 검사
npx tsc --noEmit

# 2단계: ESLint 검사
npx eslint src/ --ext .ts,.tsx

# 3단계: 프로덕션 빌드
npm run build
```

각 단계는 순서대로 실행한다. 앞 단계에서 에러가 나면 수정 후 재실행한다.

---

## 1단계: TypeScript strict 모드 검증

### 권장 tsconfig 설정

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true
  }
}
```

프로젝트에 strict 모드가 꺼져 있다면 QA 보고서에 명시한다.
strict 모드 없이 통과된 타입 검사는 신뢰도가 낮다.

### tsc 에러 파싱

```bash
npx tsc --noEmit 2>&1 | head -100
```

에러 형식:
```
src/components/UserCard.tsx(42,5): error TS2339: Property 'userName' does not exist on type 'User'.
src/hooks/useOrders.ts(18,10): error TS2322: Type 'string | null' is not assignable to type 'string'.
```

각 에러에서 추출할 정보:
- 파일 경로 + 줄 번호
- 에러 코드 (TS2339 = 존재하지 않는 프로퍼티, TS2322 = 타입 불일치)
- 에러 메시지

### 주요 에러 코드 해석

| 코드 | 의미 | 주로 나타나는 상황 |
|------|------|------------------|
| TS2339 | 존재하지 않는 프로퍼티 접근 | API 응답 shape 불일치, Tier 1 미통과 |
| TS2322 | 타입 불일치 | null 미처리, 잘못된 타입 정의 |
| TS2345 | 인자 타입 불일치 | 함수 호출부와 정의부 불일치 |
| TS2532 | 객체가 undefined일 수 있음 | optional chaining 누락 |
| TS7006 | 암시적 any | 타입 미정의 |
| TS2304 | 이름 찾을 수 없음 | import 누락, 존재하지 않는 심볼 |

### 타입 우회 코드 점검

tsc 통과만으로는 충분하지 않다. `as any`, `as unknown`으로 우회된 지점을 별도로 검사한다.

```bash
# as any 사용 전수 검색
grep -rn "as any\|as unknown\|@ts-ignore\|@ts-nocheck" src/ \
  --include="*.ts" --include="*.tsx"
```

발견된 각 위치에 대해:
- 왜 우회가 필요했는지 주석이 있는가
- 런타임에서 실제로 안전한가
- 제거 가능한 우회인가

우회 코드가 많을수록 Tier 3에서 런타임 에러 가능성이 높다.

---

## 2단계: ESLint 검사

### 실행

```bash
npx eslint src/ --ext .ts,.tsx --format compact 2>&1
```

### 중요 규칙 목록

```
no-unused-vars          — 사용되지 않는 변수 (dead code 신호)
no-console              — console.log 미제거 (개발용 코드 잔류)
react-hooks/exhaustive-deps — useEffect 의존성 배열 누락
react-hooks/rules-of-hooks  — 훅 호출 규칙 위반
no-undef                — 정의되지 않은 변수 사용
```

### 린트 에러 vs 경고 분류

- **에러**: 빌드 차단. 반드시 수정.
- **경고**: 빌드 통과. 그러나 잠재적 버그 신호. 목록 기록 후 검토.

```bash
# 에러만 필터링
npx eslint src/ --ext .ts,.tsx --quiet

# 경고 포함 전체 출력
npx eslint src/ --ext .ts,.tsx
```

### react-hooks/exhaustive-deps 에러 주의

이 에러는 단순 린트 위반이 아니라 실제 버그를 나타낼 수 있다.

```tsx
// 위험: userId가 바뀌어도 effect가 재실행되지 않음
useEffect(() => {
  fetchUserData(userId);
}, []); // 경고: userId 누락
```

---

## 3단계: 프로덕션 빌드

### 실행

```bash
npm run build 2>&1
```

### 빌드 성공 기준

```
✓ 컴파일 완료 (에러 0개)
✓ 번들 생성 완료
✓ 정적 파일 export 완료 (SSG 사용 시)
```

### 빌드 경고 확인

빌드가 통과해도 경고가 있으면 기록한다:

```bash
npm run build 2>&1 | grep -i "warn\|warning"
```

주요 경고 유형:
- 번들 크기 초과 (성능 문제)
- Deprecated API 사용
- 환경 변수 누락 (런타임에서 undefined)

### 환경 변수 누락 점검

```bash
# 코드에서 사용하는 환경 변수 추출
grep -rn "process.env\.\|import.meta.env\." src/ --include="*.ts" --include="*.tsx" \
  | grep -oP "(?<=process\.env\.)\w+|(?<=import\.meta\.env\.)\w+" | sort -u

# .env.example 또는 .env 파일과 비교
cat .env.example
```

코드에서 사용하지만 `.env.example`에 없는 변수는 배포 시 undefined가 된다.

---

## 빌드 통과 ≠ 정상 동작

Tier 2를 통과해도 다음은 발견할 수 없다:

| 발견 불가 항목 | 이유 |
|--------------|------|
| API 서버 응답 에러 | 런타임에만 발생 |
| 비동기 타이밍 버그 | 실행해봐야 알 수 있음 |
| 렌더링 깨짐 | 브라우저에서만 확인 가능 |
| 권한 우회 | 실제 요청으로만 테스트 가능 |
| 경쟁 조건(race condition) | 특정 타이밍에서만 발생 |

이런 버그들은 Tier 3에서 잡는다.

---

## Tier 2 보고서 형식

```
## Tier 2 빌드/타입 검증 결과

### TypeScript
상태: PASS / FAIL
에러 수: N개
주요 에러:
  - src/components/Card.tsx:42 — TS2339: Property 'title' does not exist
  - src/hooks/useData.ts:18 — TS2322: Type 'null' is not assignable to 'string'

타입 우회 코드:
  - src/api/client.ts:5 — as any (API 응답 임시 처리, 위험)
  - src/utils/transform.ts:12 — @ts-ignore (이유 미기재, 검토 필요)

### ESLint
상태: PASS / FAIL
에러 수: N개 | 경고 수: M개
주요 에러:
  - src/pages/index.tsx:8 — no-unused-vars: 'data' is defined but never used
주요 경고:
  - src/hooks/useOrder.ts:22 — react-hooks/exhaustive-deps: orderId 누락

### 빌드
상태: PASS / FAIL
소요 시간: Xs
번들 크기: XXX kB
경고:
  - WARNING: chunk size exceeds 500 kB (성능 검토 필요)
  - WARNING: NEXT_PUBLIC_API_URL not found in environment

### 종합 판정
Tier 3 진행 가능 여부: YES / NO
미수정 시 Tier 3 영향: [설명]
```
