#!/usr/bin/env bash
# 가정 공개 목록에 사용자가 정정을 주면, riff가 그 '물어볼 것'을 사용자 단위 업종 팩(~/.riff/domains/)에 남기는지 본다.
set -euo pipefail
git init -q
mkdir -p _workspace/detail .riff
touch _workspace/.riff-bootstrap-skip-all
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 강아지 미용샵 예약·손님 관리
> 마지막 갱신: Cycle 0 · FRAME · 2026-10-28

## STATUS
- 현재: Cycle 0 · FRAME (만들기 전 가정 공개 — 사용자 답 대기)
- depth 프로파일: 복잡 (신호 2/8)
- 활성 가정: 아래 가정 목록 — 틀린 것만 말해달라고 요청함
- 다음 액션: 가정 정정 반영 → 성공 기준 확정 → 구현

## [1] FRAME — 문제와 성공 기준 (draft · Cycle 0)
- 사용자: 1인 강아지 미용샵 원장
- 핵심 Job: 예약을 놓치지 않고, 손님(보호자)과 강아지 정보를 한 곳에서 본다
- 가정 목록(사용자에게 보여줌):
  1. 가격은 견종·체중 구간별 고정가
  2. 예약금은 받지 않음
  3. 미용은 매장에서만 함
  4. 미용 사진은 보호자에게 카톡으로만 보냄
CANVAS
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-0: frame assumptions"
