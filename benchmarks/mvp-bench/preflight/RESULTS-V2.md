# Preflight v2 — 개편된 FRAME 재실행 결과

> 2026-08-07. baseline(`runs/`)과 v2(`runs-v2/`)를 **동일한 채점기**로 다시 재고 비교했다.
> 이 결과도 실제 사용자 증거가 아니며 공식 비교표에 합산하지 않는다.

## 통제와 교란

| | baseline | v2 |
|---|---|---|
| FRAME 질문 체계 | 개편 전 | 개편 후(게이트 태그·Router 전진·리디렉션 규칙) |
| 페르소나·첫 요청·행동 제한 | 동일 | 동일 |
| acceptance 공개 | 비공개 | 비공개 |
| 채점기 | **동일**(구현 독립 버전으로 양쪽 재채점) | 〃 |
| 실행자 | Codex 서브에이전트 | **Claude 서브에이전트** ← 교란 |

실행자가 다르므로 **점수 차이를 질문 개편의 효과로 귀속할 수 없다.** 질문 개편의 직접
증거는 점수가 아니라 FOUNDER_LOG의 질문 수와 실제 발화 내용이다.

## 채점 결과

| Run | baseline | v2 | critical 변화 |
|---|---|---|---|
| a-salon | 4/8 (crit 2: expected-revenue, persistence) | 4/8 (crit 2: 동일) | 0 |
| b-reviews | 6/8 (crit 2: processing-status, persistence) | 5/8 (crit 3: +sentiment-theme) | **−1 악화** |
| c-quotes | 5/9 (crit 4: line-items, vat-total, search-filter, print-view) | 7/9 (crit 2: vat-total, search-filter) | **+2 개선** |
| **합계** | **15/25, critical 8** | **16/25, critical 7** | +1 pass, −1 critical |

**총점 기준으로는 개선이라 부를 수 없다.** 한 실행만 뚜렷이 좋아졌고, 하나는 나빠졌다.

## 질문 수 (개편의 직접 효과)

| Run | baseline | v2 |
|---|---|---|
| a-salon | 3 | 15 |
| b-reviews | 0건 기록(로그 형식 상이) | 20 |
| c-quotes | **2** | 16 |

baseline c-quotes는 depth를 '보통'으로 자가판정해 핵심 질문 2개만 던지고 acceptance 3개를
동결했다. VAT·인쇄·검색·수량/단가는 전 산출물에서 **단 한 번도 언급되지 않았다**(grep 0건).
v2에서는 같은 항목이 전부 인터뷰에 등장했다.

## 남은 실패의 성격 — 산출물 대조로 확정

초판에서 이 절을 "PROVE 간극(동결했는데 구현 안 됨)"으로 적었으나, 각 run의 동결
acceptance·FOUNDER_LOG·앱 소스를 대조한 결과 **그 진단은 틀렸다.** 세 run 모두
**동결한 것은 실제로 구현·검증했다.** 실제 원인은 동결 목록 자체의 누락이다.

| 실패 | 동결됐나 | 물었나 | 실제 원인 |
|---|---|---|---|
| a-salon `expected-revenue` | A-006에 nice-to-have로만 | 예 (13회 언급) | 우선순위 강등 |
| a-salon `persistence` | **아니오** | 아니오 | 동결 누락 |
| b-reviews `processing-status` | **아니오** | 아니오 | 동결 누락 |
| b-reviews `sentiment-theme` | **아니오** | 아니오 | 동결 누락 |
| b-reviews `persistence` | A-004로 동결·구현 | 예 | **채점 종속** — 상태 컨트롤이 없어 상태 지속을 못 잼 |
| c-quotes `vat-total` | 제외(K-003 간이과세자) | 예 | 과제 모호성 |
| c-quotes `search-filter` | **아니오** | 아니오 | 동결 누락 |

- c-quotes PROVE 기록: `node test/calc.test.js 9/9`, Playwright 스모크로 A-001~A-010 검증.
  **완료 선언은 과잉이 아니었다** — 동결한 범위 안에서는 정직했다.
- b-reviews `persistence`는 앱이 localStorage를 쓰고 A-004도 통과하지만, 채점기가 재는 것은
  *상태* 지속이라 상태 컨트롤 부재(`processing-status`)의 파생 실패다. 독립 결함이 아니다.

## 진짜 원인 — core-closure 매트릭스가 강제되지 않는다

동결 누락 4건은 전부 `discovery-research.md`에 **이미 존재하는** core-closure 행에 대응한다.

| core-closure 행 | 대응 실패 |
|---|---|
| 상태 — 생성부터 완료·취소까지의 전환 | b-reviews `processing-status` |
| 계산 — 금액·요약의 기준 | a-salon `expected-revenue` |
| 다시 찾기 — 검색·필터·정렬 | c-quotes `search-filter` |
| 다시 열기 — 새로고침 후 남아야 할 데이터 | a-salon `persistence` |
| 전달 — 인쇄·공유·내보내기 | c-quotes `print-view`(baseline) |

표는 옳다. 강제가 없을 뿐이다. `domain-intelligence.md` trace gate는
"관련 있는 core-closure 행에 `blocked`가 없다"고만 요구하므로, **행을 아예 보지 않으면
blocked도 아니고 부재도 아닌 상태로 통과한다.** 게이트 태그를 선언만 하고 수집 질문을
두지 않았던 것과 정확히 같은 결함이다.

"새로고침하면 데이터가 남아야 한다"는 **사용자가 절대 말하지 않지만 모든 웹앱이 필요한**
요구다. 이런 항목은 인터뷰를 늘려서가 아니라 닫힘 검사로만 잡힌다.

## 판정

- FRAME 개편은 **의도한 일(발굴)은 했다**: 질문 2~3개 → 15~20개, 이전에 전혀 등장하지 않던
  VAT·인쇄·항목 단가가 인터뷰에 올라왔고 c-quotes critical이 4→2로 줄었다.
- 그러나 **발굴의 완결성이 없다.** 무엇을 물었는지는 늘었지만, 무엇을 안 물었는지를
  검사하는 장치가 없다.
- 다음 작업은 PROVE 강화가 아니라 **core-closure 7행의 처분 강제**다: 각 행이
  `A-NNN 동결` / `K-NNN 근거로 제외` / `해당 없음+사유` 중 하나로 끝나야 FRAME verdict을
  통과시킨다. 기존 Knowledge Ledger와 trace gate를 재사용하며 새 시스템은 만들지 않는다.

## 채점기 변경 (중요)

기존 `riff_preflight_playwright.py`는 baseline 앱의 DOM(정확한 라벨 문자열, `#revenue`,
`.review-card`)에 결합돼 있어 다른 앱을 채점하면 `TimeoutError`로 죽었다. 공식 벤치는
riff·GSD·gstack 세 하네스의 앱을 같은 자로 재야 하므로 **이 상태로는 human pilot을 채점할 수
없었다.** 의미 기반 로케이터(라벨·placeholder·name·id 정규식) + 결과 기반 판정으로 교체했고,
baseline 판정이 정확히 재현되는 것(15/25, critical 8, 동일 ID)을 회귀 게이트로 확인했다.
