#!/usr/bin/env bash
# riff는 canvas-lint로 "done인데 코드·커밋 앵커 없음"을 거부한다 → 실제 코드와 커밋까지 만든다.
set -euo pipefail
git init -q
mkdir -p _workspace .riff src
cat > src/booking.js <<'JS'
// A-003 예약 등록 — 새로고침 후에도 남도록 localStorage에 저장
export function addBooking(list, booking) {
  const next = [...list, { ...booking, noShow: false }];
  localStorage.setItem("bookings", JSON.stringify(next));
  return next;
}
JS
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 미용실 예약
> 마지막 갱신: Cycle 1 · BUILD · 2026-10-19

## STATUS
- 현재: Cycle 1 · BUILD
- 성공 기준 진행도: 1/3
- depth 프로파일: 보통 (신호 4/8)
- 활성 가정: 없음
- 다음 액션: A-004 노쇼 기록 화면 구현 (예약 목록에 고객별 노쇼 횟수 표시)

## [1] FRAME — 문제와 성공 기준
- 핵심 Job: 원장이 하루 예약과 노쇼를 한 화면에서 관리
- A-003 예약 등록 / A-004 노쇼 기록 / A-005 새로고침 후 유지

## [3] BUILD — 계약 + 태스크 보드
| 태스크 | 근거 | 등급 | 상태 |
|---|---|---|---|
| 예약 등록 폼 (`src/booking.js`) | A-003 | core | done |
| 노쇼 기록 화면 | A-004 | core | active |
CANVAS
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-1: 예약 등록 폼"
printf '{"cycle": 1, "last_anchor": "%s"}\n' "$(git rev-parse --short HEAD)" > .riff/state.json
