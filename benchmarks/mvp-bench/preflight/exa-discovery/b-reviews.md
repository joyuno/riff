## Core-closure 적용 결과

| 행 | 미확인 핵심 |
|---|---|
| 기록·실수 | 리뷰 식별자와 필수 데이터, 누락·중복 여부 |
| 계산 | “지금 먼저”의 우선순위 기준 |
| 다시 찾기 | 분석 결과에서 근거 리뷰까지 확인할 범위 |
| 상태·다시 열기·전달 | 후속 질문으로 보류 — 현재 3개보다 우선순위가 낮음 |

### 가장 먼저 확인할 질문 3개

1. **리뷰 한 건마다 `고유 ID·상품 식별자/상품명·작성일·별점·본문`이 모두 있나요?**  
   Google의 공식 리뷰 피드도 이 값들을 리뷰 식별·상품 연결·분석의 핵심으로 사용하므로, 빠진 값이나 중복 리뷰가 있으면 가능한 분석이 달라집니다.  
   **답:** 모두 있음 / 빠진 항목 명시 / 잘 모르겠음  
   [근거: Google Product Review Feed Schema](https://developers.google.com/product-review-feeds/schema)

2. **“지금 먼저 고칠 문제”를 무엇으로 판단해야 하나요?**  
   실제 리뷰 분석 도구는 `부정 언급이 많은 주제`, `최근 악화 폭`, `리뷰가 많은 상품의 낮은 평점`을 서로 다른 지표로 제공합니다.  
   **답:** ① 부정 언급 빈도 ② 최근 악화 폭 ③ 상품별 리뷰량·평점 ④ 별도 기준 명시 ⑤ 잘 모르겠음  
   [근거: Trustpilot Topics](https://help.trustpilot.com/s/article/Trustpilot-Analytics-Review-Insights-Topics?language=en_US), [Product Review Ratings](https://help.trustpilot.com/s/article/Trustpilot-Analytics-Product-review-ratings?language=en_US)

3. **선정된 문제를 클릭했을 때 관련 원문 리뷰와 근거 문장을 확인하고, 기간·상품·별점으로 좁혀볼 필요가 있나요?**  
   주제 분류는 오분류될 수 있어 실제 도구도 관련 리뷰, 강조 문장, 기간·별점·감정 필터를 함께 제공합니다.  
   **답:** 필요 / 이번에는 제외 / 잘 모르겠음  
   [근거: Trustpilot Topics](https://help.trustpilot.com/s/article/Trustpilot-Analytics-Review-Insights-Topics?language=en_US)

여기서 멈춥니다.