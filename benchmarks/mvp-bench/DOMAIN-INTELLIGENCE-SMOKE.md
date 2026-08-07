# Domain Intelligence Smoke Test

> 실행일: 2026-08-07  
> 실행: 새 Codex thread, Riff 1.0.0, 번들 Exa  
> 과제: 반려동물 복약 일정·이상반응 기록 앱의 FRAME만 수행

## 결과

- Router: `regulated` + `safety` overlay 선택
- Domain Profile: 생성
- Domain Model: Actors·Jobs·Artifacts·Lifecycle·Rules·Exceptions·Unknowns 생성
- Knowledge Ledger: K-001~K-008, evidence state·관할·기준일·blocked 상태 생성
- 안전 경계: 앱이 누락·구토·과량 투약의 재투여 규칙을 임의 생성하지 않도록 질문
- trace gate: 사용자 확인 전 acceptance와 BUILD를 동결

## 발견한 비용 문제

초기 구현은 core-closure 검색 템플릿을 각각 실행해 Exa 검색 호출이 과해졌다. 이에
`discovery-research.md`에 초기 3개 결정 질문만 검색하고, 근거 부재·관할 불일치·출처
충돌·새 위험 overlay가 있을 때만 확장하는 조건을 추가했다. 고정 시간 제한은 두지 않는다.

## 판정

Router→Exa→Domain Model→Knowledge Ledger→재질문 흐름은 실제 새 thread에서 동작했다.
사용자 답변 뒤 K-ID가 A-ID와 PROVE까지 이어지는 전체 trace는 다음 human pilot에서
검증해야 한다.
