#!/usr/bin/env bash
# 사용자가 실수 경험을 말하지 않은 상태에서 "바로 만들어줘"라고 하면, riff가 가정 공개에
# 잘못 바꾼 상태·기록 되돌리기 기본값을 먼저 넣는지 본다(여러 턴 테스트: freelancer status-undo 누락).
set -euo pipefail
git init -q
mkdir -p _workspace/detail .riff
touch _workspace/.riff-bootstrap-skip-all
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 프리랜서 견적·진행 관리
> 마지막 갱신: Cycle 0 · FRAME · 2026-10-28

## STATUS
- 현재: Cycle 0 · FRAME (인터뷰 진행 중)
- depth 프로파일: 복잡 (신호 2/8)
- 활성 가정: 없음
- 다음 액션: 인터뷰 마무리 → 성공 기준 확정

## [1] FRAME — 문제와 성공 기준 (draft · Cycle 0)
- 사용자: 프리랜서 디자이너 1인
- Q1 답: 견적서는 엑셀로 만들어 카카오톡으로 이미지 전송. 고객 약 120명은 구글시트에 있음
- Q4 답: 어느 고객이 어디까지 진행됐는지 헷갈려서 놓친 적 있음
- 핵심 Job: 견적을 빨리 만들어 보내고, 고객별 진행 상태를 한눈에 본다
CANVAS
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-0: frame draft"
