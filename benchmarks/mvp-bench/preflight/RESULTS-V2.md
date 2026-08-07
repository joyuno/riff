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

## 남은 실패의 성격이 바뀌었다

개편 전 실패는 전부 "묻지 않아서 몰랐다"였다. v2의 잔여 실패는 세 종류로 갈린다.

1. **물었고, 근거를 남기고, 제외했다 — 과제 모호성**
   `runs-v2/c-quotes/_workspace/detail/acceptance/cycle-0.md`:
   `부가세(VAT) 별도 계산·표시 — K-003 제외 (간이과세자)`
   질문은 나왔고 Knowledge Ledger에 근거까지 남았는데, 합성 창업자가 페르소나 파일에 없는
   사실(간이과세자)을 즉흥으로 답해 제외로 확정됐다. hidden acceptance는 VAT 10%를 요구하므로
   채점은 실패다. **이건 riff의 실패가 아니라 벤치 설계의 공백**이다 — `RESULTS.md`가 이미
   예고한 "공개 과제와 답변 카드를 사전 고정" 미비 항목이며, `판정 제외/과제 모호성`으로
   분류해야 한다.
2. **물었고 동결했는데 구현이 안 됐다 — PROVE 간극(미해소)**
   v2 c-quotes CANVAS: `성공 기준 진행도: 10/10 acceptance 구현·Playwright 실브라우저 검증 완료`.
   그런데 독립 채점은 critical 2건 실패. **완료 선언 과잉이 개편 전과 동일하게 남아 있다.**
3. **질문이 늘어도 안 잡힌 것** — b-reviews는 질문 20개에도 persistence·processing-status가
   그대로 실패했고 sentiment-theme이 새로 실패했다. 질문 수는 품질의 대리지표가 아니다.

## 판정

- FRAME 개편은 **의도한 일(요구사항 발굴)은 했다**: 질문 2~3개 → 15~20개, 이전에 전혀
  등장하지 않던 VAT·인쇄·검색·항목 단가가 인터뷰에 올라왔고 c-quotes critical 실패가 절반으로 줄었다.
- 그러나 **제품 품질의 병목은 FRAME에서 BUILD·PROVE로 옮겨갔을 뿐 사라지지 않았다.**
  물어서 동결한 acceptance조차 구현되지 않은 채 완료로 선언된다.
- 다음 작업은 질문을 더 늘리는 게 아니라 **PROVE가 동결된 acceptance를 실제로 실행·차단하게
  만드는 것**이다(K-ID → A-ID → Tier 2 실행 강제).

## 채점기 변경 (중요)

기존 `riff_preflight_playwright.py`는 baseline 앱의 DOM(정확한 라벨 문자열, `#revenue`,
`.review-card`)에 결합돼 있어 다른 앱을 채점하면 `TimeoutError`로 죽었다. 공식 벤치는
riff·GSD·gstack 세 하네스의 앱을 같은 자로 재야 하므로 **이 상태로는 human pilot을 채점할 수
없었다.** 의미 기반 로케이터(라벨·placeholder·name·id 정규식) + 결과 기반 판정으로 교체했고,
baseline 판정이 정확히 재현되는 것(15/25, critical 8, 동일 ID)을 회귀 게이트로 확인했다.
