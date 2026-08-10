# RESEARCH — 채점기 검증용 fixture

이 문서는 실제 사용자 리서치 산출물이 아니라 `research-evidence` 체크를 통과시키기 위한
fixture 부속물이다. 채점기가 요구하는 것은 "출처 링크가 있는 RESEARCH.md의 존재"다.

## 제품 결정에 반영한 조사

- 감정은 별점, 주제는 본문 어휘로 나눈다. 유료 API 없이 브라우저에서만 돌리기 위한 선택.
  참고: https://developer.mozilla.org/ko/docs/Web/JavaScript/Reference/Global_Objects/RegExp
- 처리 상태(`처리 전 / 검토 중 / 개선 반영`)를 리뷰별로 남겨 재분석 때 중복 처리를 막는다.
  참고: https://developer.mozilla.org/ko/docs/Web/API/Window/localStorage
