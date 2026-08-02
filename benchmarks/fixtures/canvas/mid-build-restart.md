# 시나리오: BUILD 도중 강제 종료 후 재시작 (dirty exit)

설정: Cycle 3 BUILD에서 태스크 2/4 완료 상태의 CANVAS.md + 태스크 보드 + 커밋 앵커 cycle-2까지 존재.
세션 강제 종료 후 새 세션 시작.

기대 동작: STATUS 로드 → canvas-lint 술어 1·2 어긋남 감지 → 재조정 후 태스크 3부터 재개.
실패 판정: 완료된 태스크 재작업, 또는 Cycle 헤더/보드 불일치 방치.
