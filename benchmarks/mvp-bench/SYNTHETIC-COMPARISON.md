# Synthetic Harness Comparison — Provisional

> Execution: AI founder personas  
> Harnesses: Riff, GSD Core, gstack  
> Grading: maintainer-operated code and self-test inspection  
> Browser grading: Riff 3개 앱은 제한 없는 로컬 터미널에서 실행됨  
> Human evidence: none

이 문서는 사용자가 로컬 결과물을 직접 비교하기 위한 예비 기록이다. 공식 human pilot
결과나 순위가 아니며 README의 우월성 주장에 사용할 수 없다.

## 실행 상태

| 프로젝트 | Riff | GSD | gstack |
|---|---|---|---|
| 예약 시스템 | synthetic 완료, 자체 테스트 통과 | synthetic 완료, 4개 테스트 통과 | synthetic 완료, 2개 테스트 통과 |
| 리뷰 인사이트 | synthetic 완료, 3개 테스트 통과 | synthetic 완료, 자체 검사 통과 | synthetic 완료, 자체 검사 통과 |
| 견적 관리 | synthetic 완료, 자체 검사 통과 | synthetic 완료, 자체 검사 통과 | synthetic 완료, 자체 검사 통과 |

자체 테스트 통과는 hidden acceptance 통과를 의미하지 않는다.

## Riff Playwright 결과

| 프로젝트 | Critical 표시 결과 | 판정 보정 |
|---|---:|---|
| 예약 시스템 | 3/5 | persistence는 날짜 화면이 오늘로 초기화돼 생긴 grader 오탐이다. 저장 자체는 구현돼 있어 실제 4/5다. |
| 리뷰 인사이트 | 5/7 | 처리 상태와 그 영속성이 실제로 없다. |
| 견적 관리 | 4/8 | 항목형 견적, VAT, 검색/필터, 인쇄 화면이 실제로 없다. |

예약 시스템의 0원·과거 날짜 차단도 실패했지만 현재 grader에서는 non-critical로 잘못
분류돼 있다. 이 두 항목은 task 답변 카드의 명시 요구이므로 공식 grader에서는 critical로
올려야 한다.

## 독립 잠정 판정

### 예약 시스템

| Harness | 확인된 강점 | Critical 차이 |
|---|---|---|
| Riff | 예약·충돌·상태·영속성 | 예상 매출 대신 완료 매출 |
| GSD | 예약·충돌·상태·영속성·노쇼 이력 | 연락처·가격·예상 매출 없음 |
| gstack | 연락처·예약·충돌·상태·영속성·노쇼 이력 | 가격·예상 매출 없음 |

### 리뷰 인사이트

| Harness | 확인된 강점 | Critical 차이 |
|---|---|---|
| Riff | 감정·주제·필터·요약 | 처리 상태와 영속성 없음 |
| GSD | 반복 불만 순위·원문 근거 | 감정/주제 필터·처리 상태·영속성 없음 |
| gstack | 반복 불만 순위·원문 근거 | 감정/주제 필터·처리 상태·영속성 없음 |

### 견적 관리

| Harness | 확인된 강점 | Critical 차이 |
|---|---|---|
| Riff | 상태·예상/승인 매출·영속성 | 항목형 견적·VAT·검색·인쇄 없음 |
| GSD | 여러 항목·수량·단가·4개 상태·상태 필터·영속성 | VAT·고객 검색·매출 금액 요약·인쇄 없음 |
| gstack | 생성·상태 진행·승인 금액 | 항목형 견적·VAT·거절·필터·영속성·인쇄 없음 |

현재 코드 검사 기준으로 critical 요구를 모두 만족한 결과는 없다. GSD 견적 관리가 해당
과제 요구에 가장 가까웠지만 성공 판정은 아니다.

## 실행 개입과 한계

- Riff 세 실행은 앞선 preflight 결과를 그대로 복사했다.
- GSD 리뷰 실행은 리서치 뒤 정지해 별도 AI finisher가 기존 GSD 산출물을 이어 구현했다.
- GSD 견적 실행은 최초 자체 테스트 실패 후 별도 AI finisher가 수정했다.
- gstack 리뷰 실행은 preamble이 장시간 진행되지 않아 skill 방법론을 직접 적용하도록
  재지시했다. 견적 실행도 같은 비대화식 방법을 사용했다.
- 세 harness 모두 실제 초심자가 조작하지 않았다.
- Codex sandbox에서는 localhost와 Chromium이 차단됐지만 제한 없는 로컬 터미널에서
  Riff 세 앱의 클릭·새로고침·390px 검증 결과를 생성했다.

따라서 이 데이터는 harness 순위가 아니라 human pilot과 grader에서 잡아야 할 실패
패턴을 확인하는 용도로만 사용한다.

## Playwright

Riff 세 앱용 live grader는 `grader/riff_preflight_playwright.py`에 구현했다.

```bash
python3 benchmarks/mvp-bench/grader/riff_preflight_playwright.py
```

Codex sandbox에서는 Chromium Mach rendezvous 권한 오류로 실행되지 않는다. 제한 없는
로컬 터미널 실행은 성공했고 `preflight/results/*.playwright.json`을 생성했다.
