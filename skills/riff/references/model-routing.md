# 모델 라우팅

원칙: ① 티어 별칭(`opus`/`sonnet`/`haiku`)만 — 특정 버전 고정 금지(항상 최신 자동).
② **스폰 조건**: 서브에이전트 스폰은 정당화된 경우만 — 잼 · 동시 BUILD 태스크 ≥2 · 컨텍스트 압박.
그 외 순차 태스크·기계적 검증(Tier 0~2)·LEARN 기록은 메인 루프 인라인. 게이트 기준은 실행 위치와 무관하게 동일.

| 위치 | 모델 | 방식 |
|---|---|---|
| FRAME·SHAPE (기획) | 최상위 티어 권장(사용자가 /model로 설정한 메인 모델) | 메인 루프 인라인 — 다른 모델이면 STATUS에 권장 안내 1줄 |
| SHAPE 잼 | `opus` | 스폰 |
| BUILD core (병렬) | `opus` | 스폰 |
| BUILD support (병렬) | `sonnet` | 스폰 |
| BUILD trivial (병렬) | `haiku` | 스폰 (동시 슬롯 상한 미포함) |
| BUILD (순차) | — | 메인 루프 인라인 |
| PROVE Tier 0~2 | — | 메인 루프 인라인 |
| PROVE Tier 3 (유령·파괴자) | `sonnet` | 스폰 (격리 가치) |
| PROVE diff-review (복잡/core) | `sonnet` | 스폰 (fresh-context 가치) |
| DROP 보안 딥스캔(`drop.md`) | `sonnet` | 스폰 (보안 플래그 시 1회) |
| TUNE 스톡테이크(`tune.md`) | `sonnet` | 스폰 (fresh-context 가치) |
| LEARN | — | 메인 루프 인라인 |

**컨텍스트 압박 예외**: 인라인 지정 행(BUILD 순차·PROVE Tier 0~2·LEARN)도 컨텍스트 압박 시 스폰으로 승격 가능 — 모델은 해당 태스크 등급을 따르고, 게이트 기준은 동일하다.

등급은 BUILD-PLAN에서 태스크 보드에 명시 → 사용자가 스폰 전 오버라이드 가능(`build.md`).
