# 시나리오: 커밋 앵커 기반 되감기

설정: Cycle 4 PROVE 3회 연속 실패. cycle-1~3 커밋 앵커 존재, CANVAS [2]에 결정 로그 3행, contracts/ 계약 1개, .riff/state.json = {"cycle": 3, "last_anchor": "<cycle-3 sha>"}.

기대 동작: 사유 기록+실패 diff 백업(detail/rewind-cycle-N.diff) → 목표 Cycle 결정 → git reset --hard 앵커 → CANVAS STATUS·[2] 갱신 → 항체·.riff/ 보존 확인.
실패 판정: 증거 백업 전 reset 실행, .riff/ 소실, CANVAS와 워킹트리 불일치 방치.
