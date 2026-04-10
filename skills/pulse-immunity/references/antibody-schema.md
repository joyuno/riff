# Antibody Schema: 항체 파일 스키마 상세

---

## YAML Frontmatter 필드

```yaml
---
name: {항체명}
type: {boundary|logic|ui|performance|security}
severity: {critical|high|medium|low}
discovered: {YYYY-MM-DD}
recurrence: {재발 횟수, 숫자}
last_seen: {마지막 발견 날짜, YYYY-MM-DD}
status: {active|weakened|dormant}
---
```

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | 필수 | 항체 고유명. 파일명과 일치. 영문 소문자, 하이픈 구분 |
| `type` | enum | 필수 | 버그가 발생한 경계면 유형 |
| `severity` | enum | 필수 | 버그의 영향도 |
| `discovered` | date | 필수 | 최초 발견일 (YYYY-MM-DD) |
| `recurrence` | integer | 필수 | 총 재발 횟수. 최초 생성 시 0 |
| `last_seen` | date | 필수 | 가장 최근 발견일. 재발 시 업데이트 |
| `status` | enum | 필수 | 항체 활성화 상태 |

### type 값 정의

| 값 | 설명 | 예시 버그 |
|----|------|-----------|
| `boundary` | 에이전트/모듈 간 경계면 오류 | API 응답 shape 불일치, 타입 오류 |
| `logic` | 비즈니스 로직 오류 | 상태 전이 오류, 계산 실수 |
| `ui` | UI/UX 관련 오류 | 로딩 상태 누락, 에러 표시 안됨 |
| `performance` | 성능 관련 오류 | N+1 쿼리, 불필요한 리렌더링 |
| `security` | 보안 관련 오류 | 권한 체크 누락, 입력 미검증 |

### severity 값 정의

| 값 | 기준 |
|----|------|
| `critical` | 데이터 손실, 보안 취약점, 서비스 전체 중단 |
| `high` | 주요 기능 오작동, 데이터 불일치 |
| `medium` | 부분적 기능 오류, 엣지 케이스 실패 |
| `low` | UI 불일치, 오타, 경고 메시지 누락 |

### status 값 정의

| 값 | 설명 | BUILD 주입 |
|----|------|-----------|
| `active` | 현재 유효한 항체. 주입됨 | 예 |
| `weakened` | 90일 무재발로 약화됨. 기록만 보존 | 아니오 |
| `dormant` | 180일 무재발. 완전 비활성 | 아니오 |

---

## 섹션 구조

```markdown
---
[YAML frontmatter]
---

## 버그 설명
[무엇이 잘못되었는지. 증상 위주로 기술]

## 근본 원인
[왜 발생했는지. 에이전트의 어떤 가정이 틀렸는지]

## 예방 체크리스트
- [ ] [에이전트가 확인해야 할 항목 1]
- [ ] [항목 2]
- [ ] [항목 3]

## 관련 파일
- [파일 경로 1]
- [파일 경로 2]

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| YYYY-MM-DD | [어떤 상황에서 재발] | [체크리스트에 추가된 항목] |
```

---

## 항체 예시

### 예시 1: boundary 타입 (API 응답 래핑 누락)

```markdown
---
name: api-response-wrapping
type: boundary
severity: high
discovered: 2024-03-15
recurrence: 3
last_seen: 2024-05-02
status: active
---

## 버그 설명
백엔드 에이전트가 API 응답을 직접 반환하고, 프론트엔드 에이전트는 { data: ... } 래핑을 기대하여 런타임 오류 발생.

## 근본 원인
에이전트가 계약서 없이 "당연히 data로 감싸겠지"라고 가정. 실제로는 배열을 직접 반환함.

## 예방 체크리스트
- [ ] API 응답이 type 계약서의 Response Body와 정확히 일치하는가?
- [ ] 배열 반환 시 { data: [...] }로 래핑했는가, 아니면 직접 반환하는가? (계약서 확인)
- [ ] 에러 응답이 { error: { code, message } } 형태인가?
- [ ] null과 빈 배열을 구분하여 처리했는가?

## 관련 파일
- src/api/routes/
- src/services/

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2024-04-01 | 결제 API 구현 시 재발 | "null vs 빈 배열 구분" 항목 추가 |
| 2024-05-02 | 알림 API 구현 시 재발 | "계약서 확인" 문구 강조 |
```

---

### 예시 2: logic 타입 (상태 전이 검증 누락)

```markdown
---
name: state-transition-guard-missing
type: logic
severity: critical
discovered: 2024-04-10
recurrence: 1
last_seen: 2024-04-28
status: active
---

## 버그 설명
주문 상태가 COMPLETED에서 CANCELLED로 전이되는 버그. 최종 상태에서 전이를 막는 가드가 없었음.

## 근본 원인
에이전트가 상태 전이 로직을 구현할 때 "금지된 전이" 목록을 확인하지 않고 입력값만 검증함.

## 예방 체크리스트
- [ ] behavior 계약서의 "금지된 전이" 목록을 모두 구현했는가?
- [ ] 최종 상태(COMPLETED, CANCELLED, FAILED)에서의 전이를 차단하는 가드가 있는가?
- [ ] 상태 변경 전 현재 상태 유효성 검사가 선행되는가?
- [ ] 동시 요청으로 인한 상태 충돌(race condition)을 고려했는가?

## 관련 파일
- src/services/order.service.ts
- src/models/order.model.ts

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2024-04-28 | 예약 시스템 구현 시 재발 | "동시 요청 충돌" 항목 추가 |
```

---

### 예시 3: ui 타입 (로딩/에러 상태 누락)

```markdown
---
name: ui-async-state-incomplete
type: ui
severity: medium
discovered: 2024-03-20
recurrence: 5
last_seen: 2024-05-10
status: active
---

## 버그 설명
비동기 작업 컴포넌트에서 로딩 상태와 에러 상태가 구현되지 않아 사용자에게 빈 화면이 표시됨.

## 근본 원인
에이전트가 성공 케이스만 구현하고 loading, error 상태를 후순위로 미루다 누락.

## 예방 체크리스트
- [ ] 데이터 로딩 중 스켈레톤 또는 스피너를 표시하는가?
- [ ] API 오류 시 에러 메시지와 재시도 버튼을 표시하는가?
- [ ] 빈 데이터(empty state) 화면이 구현되어 있는가?
- [ ] visual 계약서의 7가지 상태(default, hover, active, disabled, loading, success, error)가 모두 처리되었는가?

## 관련 파일
- src/components/
- src/hooks/useAsync.ts

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2024-03-28 | 사용자 목록 페이지 | "빈 데이터 상태" 항목 추가 |
| 2024-04-05 | 결제 내역 페이지 | "재시도 버튼" 항목 추가 |
| 2024-04-20 | 알림 목록 | "visual 계약서 7가지 상태" 항목 추가 |
| 2024-05-01 | 검색 결과 페이지 | 강화 없음 (기존 체크리스트 미확인) |
| 2024-05-10 | 대시보드 위젯 | "확인 의무" 문구 강화 |
```

---

### 예시 4: performance 타입 (N+1 쿼리)

```markdown
---
name: db-n-plus-one-query
type: performance
severity: high
discovered: 2024-02-14
recurrence: 2
last_seen: 2024-04-22
status: active
---

## 버그 설명
목록 조회 API에서 각 항목마다 추가 쿼리가 발생. 100개 항목 조회 시 101번의 DB 쿼리 실행.

## 근본 원인
ORM의 지연 로딩(lazy loading)을 이해하지 못하고 반복문 안에서 관계 데이터를 참조.

## 예방 체크리스트
- [ ] 목록 조회 시 관계 데이터를 include/join으로 한번에 가져오는가?
- [ ] 단일 API 요청당 DB 쿼리가 10개를 넘지 않는가?
- [ ] ORM 쿼리 로그를 확인하여 N+1이 발생하지 않음을 검증했는가?
- [ ] 대용량 목록 조회에 페이지네이션이 적용되어 있는가?

## 관련 파일
- src/repositories/
- src/services/

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2024-04-22 | 주문 목록 API | "쿼리 로그 검증" 항목 추가 |
```

---

### 예시 5: security 타입 (권한 체크 누락)

```markdown
---
name: missing-authorization-check
type: security
severity: critical
discovered: 2024-03-05
recurrence: 0
last_seen: 2024-03-05
status: active
---

## 버그 설명
사용자가 다른 사용자의 리소스를 ID만 알면 조회/수정 가능. 소유권 검증 없이 DB에서 직접 반환.

## 근본 원인
인증(로그인 여부)만 확인하고 인가(해당 리소스 접근 권한)를 확인하지 않음.

## 예방 체크리스트
- [ ] 리소스 조회 시 요청자의 userId와 리소스 소유자 ID를 비교하는가?
- [ ] security 계약서의 권한 매트릭스를 기준으로 접근 제어를 구현했는가?
- [ ] 관리자 전용 엔드포인트에 role 검증이 있는가?
- [ ] 에러 응답이 리소스 존재 여부를 노출하지 않는가? (404 vs 403)

## 관련 파일
- src/middleware/auth.ts
- src/api/routes/

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
```
