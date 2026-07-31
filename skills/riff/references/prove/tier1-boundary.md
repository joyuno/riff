# Tier 1: 정적 경계면 QA — 상세 가이드

경계면 정적 분석은 코드를 실행하지 않고 **양쪽 동시 읽기**로 불일치를 찾는다.
비용이 가장 낮으면서 가장 흔한 버그 유형을 잡는다.

---

## 검증 대상 1: API 응답 shape ↔ 프론트 훅 타입

### 절차

1. API 핸들러에서 응답 객체 추출

```bash
# API 응답 구조 추출
grep -rn "res.json\|return {" src/api/ src/pages/api/
grep -rn "export.*interface\|export.*type" src/types/
```

2. 프론트 훅에서 기대 타입 추출

```bash
grep -rn "useQuery\|useSWR\|useEffect.*fetch\|axios.get" src/hooks/ src/components/
```

3. 나란히 비교

```
API 응답:        { user_id: number, created_at: string, is_active: boolean }
프론트 훅 타입:  { userId: number, createdAt: string, isActive: boolean }
                                                                          ↑
                        snake_case → camelCase 변환 코드가 있는지 확인 필요
```

### 자동 추출 (AST grep)

```bash
# API 응답 객체 패턴 탐색
ast-grep --pattern 'res.json({ $$$FIELDS })'

# 프론트 인터페이스 탐색
ast-grep --pattern 'interface $NAME { $$$FIELDS }'
```

### 체크 항목

- [ ] snake_case ↔ camelCase 변환 코드 존재 여부
- [ ] 옵셔널 필드(`?`)가 양쪽에서 일치하는지
- [ ] null vs undefined 처리 일치 여부
- [ ] 배열인데 단일 객체로 받는 경우 (또는 반대)
- [ ] 중첩 객체의 depth가 양쪽에서 동일한지

### 실제 버그 사례 (SatangSlide 프로젝트)

**버그: snake/camelCase 불일치**
```
API 반환: { project_title: "...", slide_count: 5 }
훅 접근:  project.projectTitle  →  undefined (항상 undefined 반환)
증상:     카드 컴포넌트에 제목이 표시되지 않음
```

---

## 검증 대상 2: 파일 경로 ↔ href / router.push

### 절차

1. 실제 라우트 파일 목록 추출

```bash
# Next.js 기준
find src/pages src/app -name "*.tsx" -o -name "*.ts" | grep -v "_app\|_document\|api/"

# 또는 app router
find src/app -name "page.tsx" | sed 's|src/app||' | sed 's|/page.tsx||'
```

2. 코드 내 링크 전수 추출

```bash
grep -rn "href=[\"']\|router.push([\"']\|Link to=[\"']" src/ \
  --include="*.tsx" --include="*.ts" --include="*.jsx"
```

3. 교차 비교

```
실제 존재하는 경로:   /dashboard, /orders, /orders/[id], /settings
코드 내 링크:         /dashboard ✓
                      /order     ✗ (404 — /orders 가 맞음)
                      /orders/detail ✗ (404 — /orders/[id] 가 맞음)
                      /profile   ✗ (파일 없음)
```

### 자동 추출 (AST grep)

```bash
# Next.js Link 컴포넌트 href 추출
ast-grep --pattern '<Link href="$PATH">'

# router.push 추출
ast-grep --pattern 'router.push("$PATH")'
```

### 체크 항목

- [ ] 모든 `href` 값에 대응하는 페이지 파일이 존재하는지
- [ ] 동적 경로(`[id]`)를 하드코딩된 경로로 링크하는 경우
- [ ] 환경별 base URL이 하드코딩된 경우
- [ ] 조건부 렌더링으로 숨겨진 링크도 포함해서 확인

### 실제 버그 사례 (SatangSlide 프로젝트)

**버그: 404 링크**
```
코드:    <Link href="/projects/new">새 프로젝트</Link>
실제:    파일 위치가 src/pages/project/create.tsx
결과:    클릭 시 404, 사용자가 새 프로젝트를 만들 수 없음
```

---

## 검증 대상 3: 상태 전이 맵 ↔ 실제 status 업데이트 코드

### 절차

1. 설계된 상태 전이 맵 확인 (riff-dna 또는 코드 주석에서)

```
설계된 상태: draft → pending → processing → done → archived
            └────────────────────────────────→ failed (any step)
```

2. 실제 status 업데이트 코드 전수 추출

```bash
grep -rn "status.*=\|\.status\s*=" src/ --include="*.ts" --include="*.tsx"
grep -rn '"pending"\|"processing"\|"done"\|"failed"' src/
```

3. 불일치 확인

```
설계:   processing → done
코드:   status = "completed"  ← "done"이 아닌 "completed" 사용
결과:   상태 비교 로직 전체 오작동
```

### 체크 항목

- [ ] 모든 상태값 문자열이 설계와 정확히 일치
- [ ] 누락된 상태 전이 (코드에 없는 전이)
- [ ] 허용되지 않는 전이 (설계에 없는 전이가 코드에 존재)
- [ ] 상태 비교를 `===` 대신 느슨한 비교(`==`)로 하는 경우
- [ ] 상태값이 여러 파일에 중복 정의되어 불일치 위험

### 실제 버그 사례 (SatangSlide 프로젝트)

**버그: 상태전이 누락**
```
설계:   processing → done
        processing → failed
코드:   done 처리 로직만 존재, failed 분기 없음
결과:   API 오류 시 로딩 스피너가 영원히 표시됨
```

---

## 검증 대상 4: DB 스키마 ↔ API 응답 ↔ 프론트 타입 체인

### 절차

1. DB 스키마 추출

```bash
# Prisma 기준
cat prisma/schema.prisma | grep -A 20 "^model "

# SQL 기준
cat schema.sql | grep -A 5 "CREATE TABLE"
```

2. API 직렬화 레이어 확인

```bash
grep -rn "select:\|include:\|prisma\." src/api/ src/pages/api/
```

3. 프론트 타입 추출

```bash
grep -rn "interface\|type " src/types/ src/hooks/
```

4. 체인 추적

```
DB:     users.user_name (VARCHAR)
API:    { username: string }   ← 컬럼명 변환됨
프론트: user.name              ← 또 다른 이름으로 접근 → undefined
```

### 체크 항목

- [ ] DB 컬럼 → API 직렬화 → 프론트 타입까지 이름 체인 완전성
- [ ] DB에는 있지만 API가 select에서 제외한 필드를 프론트가 기대하는 경우
- [ ] DB 타입(int, varchar, bool)과 프론트 TypeScript 타입 일치
- [ ] nullable 컬럼에 대한 null 처리가 프론트에 존재하는지
- [ ] 관계(relation) 데이터 include 여부 vs 프론트의 중첩 접근

### 실제 버그 사례 (SatangSlide 프로젝트)

**버그: projects.filter 에러**
```
DB:       projects 테이블에 is_deleted 컬럼 있음
API:      select: { id, title, slides }  ← is_deleted 제외됨
프론트:   projects.filter(p => !p.isDeleted)  → undefined.filter 에러
증상:     프로젝트 목록 페이지 전체 크래시
```

**버그: 즉시응답/비동기 혼동**
```
API:      슬라이드 생성 시 즉시 { id: "..." } 반환 (백그라운드 처리)
프론트:   응답 직후 slides[0].content 접근 → undefined
이유:     content는 백그라운드 처리 완료 후에만 존재
해결:     폴링 또는 웹소켓으로 처리 완료 시점 확인 필요
```

**버그: 훅 미존재**
```
컴포넌트: useSlideEditor() 훅 호출
파일:     src/hooks/useSlideEditor.ts 없음
결과:     빌드 에러가 아닌 런타임 에러 (dynamic import 사용 중)
```

---

## 경계면 체크리스트 (웹 앱용)

### API ↔ 프론트

- [ ] 모든 API 엔드포인트의 응답 shape이 프론트 타입과 일치
- [ ] 에러 응답 형식(`{ error: string }` vs `{ message: string }`)이 일치
- [ ] 페이지네이션 구조(`{ data: [], total: number }`)가 일치
- [ ] 날짜 형식(ISO 8601 vs Unix timestamp vs custom)이 일치
- [ ] 파일 업로드 응답의 URL 필드명이 일치

### 라우팅

- [ ] 로그인 후 리다이렉트 경로가 실제로 존재
- [ ] 에러 페이지 경로(`/404`, `/500`)가 존재
- [ ] 동적 경로의 파라미터 이름이 코드와 일치(`[id]` vs `[slug]`)
- [ ] API 라우트 경로가 프론트 fetch URL과 일치

### 상태 관리

- [ ] 전역 상태의 초기값이 API 응답 타입과 호환
- [ ] 로컬 상태 업데이트 로직이 API 응답 구조에 맞게 작성됨
- [ ] 낙관적 업데이트(optimistic update) 시 롤백 로직 존재

### 인증

- [ ] 토큰 만료 시 처리 로직이 API와 프론트 양쪽에 존재
- [ ] 권한별 접근 제어가 API와 UI 양쪽에서 적용됨
- [ ] 로그아웃 시 모든 로컬 상태 초기화 확인
