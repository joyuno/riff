# Behavior Contract: {모듈명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: {에이전트명}
> 상태: draft | active | deprecated

---

## 개요

{이 계약서가 다루는 비즈니스 플로우 설명. 예: "사용자 주문 생성부터 배송 완료까지의 상태 전이 규칙"}

---

## 상태 목록

| 상태 | 설명 | 진입 조건 | 이탈 가능 여부 |
|------|------|-----------|--------------|
| `DRAFT` | 초안 상태 | 최초 생성 | 가능 |
| `PENDING` | 처리 대기 | 사용자 제출 | 가능 |
| `PROCESSING` | 처리 중 | 시스템 접수 | 불가 (완료 대기) |
| `COMPLETED` | 완료 | 처리 성공 | 불가 (최종 상태) |
| `FAILED` | 실패 | 처리 오류 | 가능 (재시도) |
| `CANCELLED` | 취소 | 사용자 또는 시스템 취소 | 불가 (최종 상태) |

---

## 상태 전이 다이어그램

```
[DRAFT] ──제출──→ [PENDING] ──접수──→ [PROCESSING] ──성공──→ [COMPLETED]
   ↑                  │                     │
   └──수정 요청──←───┘                     └──실패──→ [FAILED] ──재시도──→ [PENDING]
                  │
                  └──취소──→ [CANCELLED]
```

---

## 허용된 전이

| From | To | 조건 | 실행 주체 | 부수 효과 |
|------|----|------|-----------|-----------|
| `DRAFT` | `PENDING` | 필수 필드 모두 채워짐 | 사용자 | 이메일 발송, 로그 기록 |
| `PENDING` | `PROCESSING` | 시스템 용량 여유 있음 | 시스템 | 작업 큐 등록 |
| `PENDING` | `CANCELLED` | 사용자 요청 또는 타임아웃 | 사용자/시스템 | 환불 처리 |
| `PROCESSING` | `COMPLETED` | 처리 성공 | 시스템 | 완료 알림 발송 |
| `PROCESSING` | `FAILED` | 처리 오류 | 시스템 | 에러 로그, 알림 |
| `FAILED` | `PENDING` | 재시도 요청 (최대 3회) | 사용자/시스템 | 재시도 카운터 증가 |

---

## 금지된 전이

| From | To | 이유 |
|------|----|------|
| `COMPLETED` | 모든 상태 | 최종 상태는 불변 |
| `CANCELLED` | 모든 상태 | 최종 상태는 불변 |
| `PROCESSING` | `DRAFT` | 처리 중에는 되돌릴 수 없음 |
| `DRAFT` | `COMPLETED` | 처리 단계 생략 불가 |

---

## 유저 저니 순서

### 정상 플로우

```
1단계: 사용자가 폼 작성 (DRAFT)
   - 필수 필드: [name, email, ...]
   - 선택 필드: [phone, ...]
   - 저장은 가능, 제출은 유효성 검사 통과 후

2단계: 제출 (DRAFT → PENDING)
   - 유효성 검사 실패 시: 에러 표시, 상태 유지
   - 성공 시: 확인 이메일 발송

3단계: 시스템 처리 (PENDING → PROCESSING)
   - 사용자 개입 없음
   - UI: 진행 표시 (스피너 또는 프로그레스 바)

4단계: 완료 (PROCESSING → COMPLETED)
   - 완료 알림 표시
   - 결과 페이지로 이동
```

### 에러 플로우

```
처리 실패 (PROCESSING → FAILED):
   - 사용자에게 실패 원인 표시
   - 재시도 버튼 제공 (최대 3회)
   - 3회 실패 시: 고객센터 안내
```

---

## 비즈니스 규칙

1. **재시도 제한**: FAILED 상태에서 PENDING으로 전이는 최대 3회
2. **타임아웃**: PENDING 상태에서 24시간 내 처리 없으면 자동 CANCELLED
3. **동시성**: 동일 사용자가 동시에 PROCESSING 상태인 항목은 최대 1개
4. **권한**: CANCELLED 전이는 소유자 또는 관리자만 가능

---

## 이벤트 목록

각 전이 발생 시 발행되는 이벤트:

| 이벤트 | 발생 시점 | 페이로드 |
|--------|-----------|---------|
| `example.submitted` | DRAFT → PENDING | `{ id, userId, timestamp }` |
| `example.processing` | PENDING → PROCESSING | `{ id, timestamp }` |
| `example.completed` | PROCESSING → COMPLETED | `{ id, result, timestamp }` |
| `example.failed` | PROCESSING → FAILED | `{ id, error, retryCount, timestamp }` |
| `example.cancelled` | → CANCELLED | `{ id, reason, cancelledBy, timestamp }` |

---

## 변경 이력

| 날짜 | 변경 내용 | 변경자 |
|------|-----------|--------|
| {YYYY-MM-DD} | 최초 생성 | {에이전트명} |
