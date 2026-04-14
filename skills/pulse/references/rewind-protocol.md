# 되감기 프로토콜

VERIFY 3회 연속 실패 또는 방향 오류 감지 시 실행한다.
이 파일은 되감기 패턴 적용 시에만 읽는다.

---

## 발동 조건

다음 중 하나 충족 시 즉시 되감기 시작:

| 조건 | 판단 기준 |
|------|-----------|
| VERIFY 3회 연속 실패 | 같은 Pulse에서 수정 → 재검증을 3번 반복했으나 계속 실패 |
| 방향 오류 감지 | 구현 완료 후 "이 방향으로는 요구사항을 충족할 수 없다"고 판단될 때 |
| 계약서 위반 누적 | Tier 0에서 같은 계약서 위반이 3회 이상 반복될 때 |

---

## 되감기 절차

### 1단계: 상태 저장 (현재 Pulse)

되감기 전 현재 상태를 기록한다:

```
_workspace/pulse-N/rewind-reason.md 생성:
  - 실패한 Pulse 번호
  - 실패 원인 (VERIFY 실패 내용 / 방향 오류 설명)
  - 3회 수정 시도 내역
  - 되감기할 목표 Pulse 번호
```

### 2단계: 목표 Pulse 결정

| 실패 유형 | 되감기 목표 |
|-----------|------------|
| 구현 오류 (로직 버그) | 직전 Pulse (N-1) |
| 설계 오류 (인터페이스 잘못됨) | 계약서 생성 이전 (BUILD-CONTRACT 단계) |
| 방향 오류 (요구사항 미충족) | Pulse 0 또는 ASK 단계 |

### 3단계: state.json 복원

`.pulse/state.json`에서 목표 Pulse 시점의 상태를 로드한다:

```json
{
  "current_pulse": N-1,
  "rewind_from": N,
  "rewind_reason": "VERIFY 3회 실패: [요약]",
  "contracts_valid_at": "pulse-N-1",
  "journeys_progress": {...},
  "pending_tasks": [...]
}
```

복원 시 주의:
- `_workspace/pulse-N/`의 파일은 삭제하지 않는다 (학습 자료로 보존).
- `_workspace/contracts/`에서 Pulse N에서 추가된 계약서만 `status: reverted`로 표시.
- pulse-immunity에 되감기 원인을 항체로 등록한다.

### 4단계: LEARN 단계 강제 실행

되감기 전에 반드시 LEARN을 실행한다:

```
pulse-immunity: 실패 패턴 → 항체 생성 (severity: high 이상)
pulse-dna: 방향 오류였다면 의사결정 패턴에 기록
pulse-log.md에 되감기 이력 추가
```

### 5단계: 재시작

목표 Pulse/단계부터 다시 시작한다.
**되감기 후 첫 BUILD-PLAN에서 반드시 rewind-reason.md를 읽고 같은 실수를 방지한다.**

---

## 되감기 이력 형식 (pulse-log.md)

```markdown
## ⏪ 되감기 — Pulse N → Pulse M [날짜]

- 원인: [VERIFY 3회 실패 / 방향 오류 / 계약서 위반]
- 실패 요약: [2-3줄]
- 항체 등록: [항체명] (severity: high)
- 재시작 지점: Pulse M의 [단계]
```
