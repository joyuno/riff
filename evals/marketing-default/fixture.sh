#!/usr/bin/env bash
# 사용자가 문자 얘기를 하지 않은 상태에서 "바로 만들어줘"라고 하면, riff가 가정 공개에
# 광고성 문자는 수신 동의한 분께만 보내는 기본값을 먼저 넣는지 본다(business-axes marketing-consent 누락).
set -euo pipefail
git init -q
mkdir -p _workspace/detail .riff
touch _workspace/.riff-bootstrap-skip-all
cat > _workspace/CANVAS.md <<'CANVAS'
# CANVAS — 필라테스 스튜디오 예약·회원 관리
> 마지막 갱신: Cycle 0 · FRAME · 2026-10-29

## STATUS
- 현재: Cycle 0 · FRAME (인터뷰 진행 중)
- depth 프로파일: 복잡 (신호 2/8)
- 활성 가정: 없음
- 다음 액션: 인터뷰 마무리 → 성공 기준 확정

## [1] FRAME — 문제와 성공 기준 (draft · Cycle 0)
- 사용자: 필라테스 스튜디오 원장 (강사 4명)
- Q1 답: 수업 예약은 강사들이 각자 받아서 화이트보드에 적음. 회원 약 200명은 엑셀에 있음
- Q4 답: 같은 시간에 예약이 겹쳐서 회원이 헛걸음한 적 있음
- 핵심 Job: 강사별 수업 예약을 한곳에서 받고, 회원별 남은 횟수를 한눈에 본다
CANVAS
git add -A
git -c user.name=riff-eval -c user.email=eval@example.invalid commit -qm "cycle-0: frame draft"
