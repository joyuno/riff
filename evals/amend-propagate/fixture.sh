#!/usr/bin/env bash
# 승인된 선택(예약금)을 번복할 때 A-NNN만이 아니라 그 A-NNN을 근거로 한 [3] 태스크·contracts/까지 따라 고치는지 본다.
set -euo pipefail
git init -q
mkdir -p _workspace/contracts .riff
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 미용실 예약
> 마지막 갱신: Cycle 1 · BUILD · 2026-10-19

## STATUS
- 현재: Cycle 1 · BUILD > PLAN
- 성공 기준 진행도: 0/3
- depth 프로파일: 보통 (신호 4/8)
- 활성 가정: 없음
- 다음 액션: 태스크 보드 첫 행부터 구현

## [1] FRAME — 문제와 성공 기준 (approved · Cycle 1)
- 핵심 Job: 원장이 하루 예약과 노쇼를 한 화면에서 관리
- 결제: 예약 시 예약금 1만원 선결제 (사용자 선택, Q7)
- A-003 예약 등록: 이름·연락처·시간으로 예약을 만든다 (K-001)
- A-004 노쇼 처리: 노쇼가 확정되면 예약금을 몰수하고 매출에 반영한다 (K-005)
- A-005 다시 열기: 새로고침 후에도 예약·노쇼 기록이 남는다 (K-006)

## [3] BUILD — 계약 + 태스크 보드
계약: `contracts/booking.md`
| 태스크 | 근거 | 등급 | 상태 |
|---|---|---|---|
| 예약 등록 폼 | A-003 | core | todo |
| 예약금 결제·몰수 처리 | A-004 | core | todo |
| localStorage 저장 | A-005 | core | todo |
CANVAS
cat > _workspace/contracts/booking.md <<'CONTRACT'
# booking 계약

- `DEPOSIT_KRW = 10000` — 예약 시 선결제 금액 (A-004)
- `Booking { id, name, phone, time, depositPaid: boolean, noShow: boolean }`
- 상태 전이: `booked → visited` | `booked → noShow → forfeitDeposit()` (A-004)
CONTRACT
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-1: plan"
