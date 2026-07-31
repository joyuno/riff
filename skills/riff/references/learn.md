# LEARN — 항체·프로파일·커밋 앵커

실행 위치: 메인 루프 인라인. 스키마는 `learn/antibody-schema.md`·`learn/profile-schema.md`.

## 순서

1. **항체**: 이번 사이클 버그 → 항체 생성/강화. 저장 전 dedup grep(`grep -rl <핵심 패턴> .riff/memory/antibodies/`) — 기존 항체 강화가 우선, 신규는 중복 없을 때만.
2. **red-green 검증** (신규 항체 + repro 테스트 생성 시에만): fix를 임시 되돌려 repro 실패(red) 확인 → 복원 후 통과(green) 확인. 실패 재현 안 되는 repro는 폐기(거짓 면역 방지).
3. **프로파일**: 2회 반복 관찰 → 학습, 명시 피드백 → 즉시 반영 (기존 규칙 유지).
4. **도메인 brief**: 같은 도메인 태스크 ≥3 누적 시 `detail/domains/<domain>.md` ≤20줄 생성·갱신 — 이후 해당 도메인 스폰 프롬프트에 주입. 3개 도메인 초과 시 STATUS에 팀 툴 졸업 안내 1줄.
5. **CANVAS [5] + STATUS 갱신** → 확신도 기록.
6. **사이클 커밋 앵커**: clean-tree 확인(`git status --porcelain` 비어야 함 — 미추적 잔재는 정리 후) → `git add -A && git commit -m "cycle-N: <1줄 요약>"`. 이 커밋이 되감기·diff-review·canvas-lint 술어 1의 앵커다. `.riff/state.json`의 `cycle` 필드와 커밋 메시지의 N이 일치해야 한다.
7. **TUNE 발동 판단**: 마지막 TUNE 후 3~5사이클 경과 or rewind 직후 or no-progress 상한 → TUNE 제안(`tune.md`).
8. **세션 분리 판단**: 컨텍스트 압박 시 캔버스 갱신 완료 후 분리 권고.
