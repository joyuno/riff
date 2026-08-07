# Synthetic Founder Preflight — Results

> Synthetic preflight: AI founder personas  
> Human pilot: not run  
> Grading: maintainer-operated, provisional code and test inspection  
> Study: maintainer-operated, not independent

이 결과는 실제 사용자 증거가 아니며 공식 MVP Bench 비교표에 합산하지 않는다. 실행자
이름, 계정, 로컬 경로, 컴퓨터 정보와 개인 대화는 공개하지 않았다.

## 결과 요약

| Run | 자체 완료 선언 | 독립 잠정 판정 | 가장 큰 차이 |
|---|---|---|---|
| A — 예약·노쇼 | 완료 | 실패 | 예상 매출 대신 완료 매출, 과거 날짜·0원 허용 |
| B — 리뷰 인사이트 | 완료 | 실패 | 처리 상태와 영속성 없음 |
| C — 견적 관리 | 완료 | 실패 | 항목·수량·단가·VAT·검색·인쇄 없음 |

세 실행 모두 자체 검사는 통과했지만 hidden acceptance의 critical 요구를 모두 만족한
실행은 없었다. 이는 Riff 우위의 증거가 아니라, 현재 Riff의 `PROVE`와 독립적인 제품
acceptance 사이에 간극이 있다는 예비 증거다.

## 공통 관찰

1. **조사 흔적은 남았다.** 세 실행 모두 출처와 제품 결정을 연결했다.
2. **자체 테스트는 좁았다.** 구현한 로직은 검사했지만 누락된 핵심 기능은 잡지 못했다.
3. **완료 선언이 과했다.** 세 CANVAS 모두 완료로 기록됐지만 독립 기준과 불일치했다.
4. **질문 수와 품질은 달랐다.** 질문이 많아도 B의 핵심 업무 상태는 드러나지 않았고,
   C는 적은 질문 뒤 다른 제품 정의로 수렴했다.
5. **브라우저 증거는 없다.** 반응형 CSS는 존재하지만 실제 클릭·새로고침·390px 동작은
   이번 환경에서 검증하지 못했다.

## 벤치 설계에 반영할 변경

- 공개 과제와 답변 카드가 critical 요구를 일관되게 드러내도록 사전 고정한다.
- 실행 도구의 완료 선언과 별도로 외부 grader가 통과해야 성공으로 기록한다.
- “구현하지 않은 요구”도 잡는 acceptance를 만들고, 자체 테스트 통과와 분리해 표시한다.
- 공개 과제로 유도되지 않은 기준은 실패가 아니라 `판정 제외/과제 모호성`으로 기록한다.
- 공식 실행 전 브라우저·로컬 서버가 동작하는 runner를 검증한다.

## 실패 분류

| 관찰 | 분류 |
|---|---|
| A의 예상 매출·경계값 누락 | app defect + Riff workflow failure |
| B의 처리 상태·영속성 누락 | app defect + Riff workflow failure |
| B의 빈 리뷰 입력 기준 | acceptance-check weakness + task ambiguity |
| C가 견적 현황판으로 수렴 | task ambiguity + Riff workflow failure |
| 세 CANVAS의 조기 완료 선언 | Riff workflow failure |
| 실제 브라우저 검증 불가 | benchmark infrastructure defect |
| AI 페르소나의 잠재 개발 지식 | synthetic-method limitation; persona leakage 증거는 확인되지 않음 |

## 제한

- AI 페르소나는 실제 초심자가 아니다.
- Riff만 실행한 preflight이며 GSD·gstack 비교 결과가 아니다.
- 브라우저 검증 전 잠정 결과다.
- 세 실행과 채점 모두 유지보수자 통제 아래 수행됐다.

세부 판정: [A](results/a-salon.md) · [B](results/b-reviews.md) · [C](results/c-quotes.md)
