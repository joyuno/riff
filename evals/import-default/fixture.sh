#!/usr/bin/env bash
# 사용자가 기존 손님 명단 얘기를 하지 않은 상태에서 "바로 만들어줘"라고 하면, riff가 가정 공개에
# 지금 쓰는 명단을 처음에 한 번에 옮겨 오는 기본값을 먼저 넣는지 본다(기존 데이터 이관 누락).
set -euo pipefail
git init -q
mkdir -p _workspace/detail .riff
touch _workspace/.riff-bootstrap-skip-all
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 미용실 디자이너별 예약 관리
> 마지막 갱신: Cycle 0 · FRAME · 2026-10-30

## STATUS
- 현재: Cycle 0 · FRAME (인터뷰 진행 중)
- depth 프로파일: 복잡 (신호 2/8)
- 활성 가정: 없음
- 다음 액션: 인터뷰 마무리 → 성공 기준 확정

## [1] FRAME — 문제와 성공 기준 (draft · Cycle 0)
- 사용자: 동네 미용실 원장 (디자이너 3명)
- Q1 답: 네이버 예약과 카톡 문의가 섞여서 같은 시간에 중복 예약이 생김
- Q4 답: 노쇼가 한 달에 몇 번씩 나서 그 시간을 그냥 비움
- 핵심 Job: 디자이너별 예약을 한곳에서 받고 노쇼를 막는다
CANVAS
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-0: frame draft"
