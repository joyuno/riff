# 전문가 통합 5-Layer 질문 흐름

이 파일은 SKILL.md의 5-Layer 실행 시 참조한다.
각 Layer에서 기본 질문 후 해당 Layer에 기여하는 전문가 질문이 이어진다.

---

## Layer 1: WHY — Job 정의 + AI 필요성 조기 탐색

**기본 질문** (JTBD):
- Q1: "이 제품이 없으면, 그 일을 지금 어떻게 하고 있나요? 가장 큰 문제는?"
- Q2: "하루가 끝날 때 '이걸 써서 다행이다' 싶은 순간은 어떤 순간인가요?"

**전문가 기여 — AI Engineer (게이트 질문)**:
- Q1-AI: "이 Job에서 반복되는 패턴이나 대량 처리가 있나요? AI/자동화가 역할을 할 수 있을 것 같나요?"
  - 예 → `ai_potential` 태그, Layer 3에서 심화 질문
  - 아니오 → `ai_none` 태그, Layer 3~4에서 AI 질문 생략

**자동 태깅**:
- 기존 방식이 느리다 → `performance_critical`
- 수동 실수가 많다 → `reliability_critical`
- 새 시장 개척 → `market_risk`
- AI 가능성 언급 → `ai_potential`

---

## Layer 2: WHO — 실제 사용자 파악 + 디바이스/경험 탐색

**기본 질문** (Mom Test):
- Q3: "이 문제를 겪는 사람을 한 명 떠올려보세요. 그 사람이 지난주에 이 문제를 어떻게 해결했나요?"
- Q4: "그 과정에서 가장 짜증났던 순간은 언제였나요?"
- Q5: "동시 사용자 규모는?" (A: 1~10명 / B: 100~1,000명 / C: 10,000명+)

**전문가 기여 — UI Designer**:
- Q2-UI: "그 사람이 주로 어떤 환경에서 쓸까요?"
  - A: PC/웹 브라우저 → `desktop_primary`
  - B: 스마트폰 앱 → `mobile_primary`
  - C: 둘 다 → `responsive_required`
- Q2-UI-b: "그 사람이 평소에 즐겨 쓰는 앱이나 서비스가 있나요? (레퍼런스 UX)"
  - 답변 → `reference_ux` 태그에 저장

**전문가 기여 — Frontend Dev**:
- Q2-FE: (Q5 규모 선택 C 일 때만) "10,000명 이상이 동시에 접속하는 상황이 자주 있나요, 아니면 특정 시간대에 몰리나요?"
  - 항상 → `scale_constant`
  - 몰림 → `scale_spike`

**자동 태깅**:
- desktop_primary / mobile_primary / responsive_required
- small_scale(~10) / medium_scale(~1k) / large_scale(10k+)

---

## Layer 3: WHAT — 핵심 범위 + 기술 범위 조기 확정

**기본 질문** (Constraint Forcing):
- Q6: "딱 하나의 화면, 하나의 버튼만 있다면 그게 뭔가요? 그 버튼을 누르면 어떤 일이?"
- Q6-확장: "거기에 2~3개를 더 추가한다면? '반드시 / 있으면 좋음 / 나중에'로 분류해주세요."
- Q7: "첫 버전을 언제까지 써보고 싶으세요?" (A: 2주 / B: 1~2개월 / C: 3개월+)

**전문가 기여 — Backend Dev**:
- Q3-BE: "방금 말씀하신 핵심 기능에서, 데이터가 저장되고 불러와야 하는 부분이 있나요?"
  - 예 → `data_persistence` 태그, Layer 4에서 DB/백엔드 질문 심화
  - 아니오 → 정적 사이트 가능성 검토

**전문가 기여 — AI Engineer** (`ai_potential` 태그 있을 때만):
- Q3-AI: "핵심 기능에서 AI가 하는 역할이 뭔가요?"
  - A: AI가 핵심 (없으면 서비스 성립 안 됨) → `ai_required`
  - B: AI가 보조 (없어도 되지만 있으면 훨씬 좋음) → `ai_optional`
  - C: 나중에 추가해도 됨 → `ai_later`

**자동 태깅**:
- must_have / nice_to_have / later
- ai_required / ai_optional / ai_later / ai_none
- data_persistence

---

## Layer 4: HOW — 기술 결정 라운드테이블 (핵심 확장, 15분)

Layer 4는 소크라테스 기본 질문 이후 전문가 기술 결정이 순서대로 이어진다.
이전 Layer 태그에 따라 관련 없는 질문은 자동 건너뜀.

**기본 질문** (소크라테스):
- Q8: "이미 익숙하거나 사용 중인 도구가 있나요?"
- Q9: [Layer 1 태깅 기반 동적 트레이드오프 질문]

---

### HOW-A: UI 디자이너 (항상 실행)

Q4-UI-1: "이 서비스의 첫인상 느낌은?"
  - A: 깔끔하고 전문적 (B2B/SaaS) → `b2b_aesthetic`
  - B: 감각적이고 트렌디 (소비자 앱) → `consumer_trendy`
  - C: 따뜻하고 친근함 (커뮤니티/교육) → `warm_friendly`
  - D: 강렬하고 임팩트 (엔터/스타트업) → `bold_impact`

Q4-UI-2: "화면 전환이나 인터랙션 수준은?"
  - A: 없거나 최소 → `animation_none`
  - B: 부드러운 전환 → `animation_subtle`
  - C: 풍부한 인터랙션 → `animation_rich`
  - D: 몰입형 (3D/Rive) → `animation_immersive`

Q4-UI-3: "필요한 것 선택: [ ] 다크모드 [ ] 접근성"

**UI 스킬 자동 추천** (태그 기반):
| 태그 조합 | 추천 스킬 |
|----------|---------|
| b2b + animation_none/subtle | shadcn/ui + Tailwind |
| consumer_trendy + animation_rich | Aceternity UI + Framer Motion |
| mobile_primary + Flutter | flutter_animate + Material 3 |
| animation_immersive | Aceternity + GSAP 또는 Rive |

추천 출력 후: "이 스킬로 진행할까요, 아니면 다른 선호가 있나요?"

---

### HOW-B: 자료 리서처 (UI 스킬 확정 직후 실행)

Q4-RR: "추천된 스킬 외에 추가로 필요한 도구 카테고리가 있나요?"
  - [ ] 테스트/QA 스킬
  - [ ] Git/배포 스킬
  - [ ] 도메인 특화 스킬
  - [ ] 없음

선택된 스킬 GitHub 리서치 후:
```
발견된 스킬:
1. [스킬명] — [설명]
   설치: claude plugin install [URL]
```
"설치할 스킬을 선택해주세요."

---

### HOW-C: 프론트엔드 개발자 (data_persistence 또는 responsive_required 태그 있을 때)

Q4-FE-1: "주요 화면 목록을 제안드릴게요. [Layer 3 핵심 기능 기반 자동 제안]
  추가하거나 제거할 화면이 있나요?"

Q4-FE-2: "화면 간 이동 방식은?"
  - A: 상단 네비게이션 (웹)
  - B: 사이드바 (대시보드)
  - C: 하단 탭 바 (모바일)

Q4-FE-3: (mobile_primary 또는 responsive_required 태그 있을 때만)
  "검색엔진 노출이 필요한가요? (SEO → Next.js SSR 필요)"

---

### HOW-D: 백엔드 개발자 (data_persistence 태그 있을 때)

Q4-BE-1: "서버 기술 스택 — [규모 태그 기반 자동 추천] 으로 진행할까요?"
  자동 추천:
  - small_scale → Node.js/Express 또는 FastAPI
  - medium_scale → FastAPI + Redis
  - large_scale → FastAPI/Go + Redis + 메시지 큐

Q4-BE-2: "로그인이 필요한가요? 필요하다면 방식은?"
  - A: 이메일/비밀번호
  - B: 소셜 (Google/Kakao/Naver)
  - C: A+B 혼합
  - D: 불필요

Q4-BE-3: "외부 서비스 연동이 필요한가요?"
  - [ ] 결제 [ ] 이메일 발송 [ ] 파일 저장 [ ] 지도 [ ] 없음

---

### HOW-E: 데이터 엔지니어 (medium_scale 이상 또는 data_persistence 있을 때)

Q4-DE-1: "1년 후 예상 데이터 규모는?"
  - A: 소 (1GB 미만) / B: 중 (10~100GB) / C: 대 (1TB+)

Q4-DE-2: "컨테이너/인프라 관리는?"
  - A: 단순 서버 / B: Docker Compose / C: Kubernetes
  (large_scale → K8s 자동 추천)

Q4-DE-3: "캐싱이나 검색 기능이 필요한가요?"
  - [ ] Redis 캐싱 [ ] 전문 검색 (Elasticsearch/Meilisearch) [ ] 없음

---

### HOW-F: DB 설계자 (data_persistence 태그 있을 때)

Q4-DB-1: "데이터 구조 특성은? (해당하는 것 선택)"
  - [ ] 계층형 (카테고리-서브, 댓글-대댓글)
  - [ ] 시간 순서 중요 (로그, 거래내역)
  - [ ] 개인정보 포함
  - [ ] 해당 없음

Q4-DB-2: "DB는 [자동 추천: 스택+규모 기반]으로 진행할까요?"
  (PostgreSQL / MongoDB / MySQL — 이전 태그 기반 선택)

---

### HOW-G: AI 엔지니어 (ai_required 또는 ai_optional 태그 있을 때만)

Q4-AI-1: "AI가 하는 일을 선택해주세요."
  - [ ] 텍스트 생성/답변
  - [ ] 문서 요약/분류
  - [ ] 내 데이터 기반 검색 (RAG)
  - [ ] 이미지 분석/생성
  - [ ] 자율 에이전트

Q4-AI-2: "AI 비용 예산은 월 얼마까지?"
  - A: 최소 ($0~$10) / B: 소 ($10~$100) / C: 중 ($100~$1,000) / D: 제한 없음

Q4-AI-3: (RAG 선택 시) "AI가 참조할 데이터는 어디에 있나요?"
  - A: 서비스 내 DB / B: 외부 문서 / C: 실시간 웹 / D: 조합

---

## Layer 5: MEASURE — 실패 시나리오 + 충돌 감지 + 최종 확정

**기본 질문** (Pre-mortem):
- Q10: "3개월 후 이 서비스가 실패했다면, 가장 가능성 높은 이유는?"
- Q10-후속: "그 실패를 막으려면 첫 달에 어떤 숫자를 봐야 하나요?"

**전문가 기여 — Prompt Engineer** (항상, 마지막):

충돌 감지:
- Layer 4 기술 결정 간 불일치 자동 탐지
- 발견 시: "A 결정과 B 결정이 충돌합니다. 어느 쪽을 우선할까요?"

P0/P1/P2 최종 확인:
```
P0 (MVP 필수): [항목]
P1 (있으면 좋음): [항목]
P2 (나중에): [항목]
"이 우선순위가 맞나요?"
```

**master-plan.md 생성** → `_workspace/pulse-0/master-plan.md`

---

## 건너뜀 로직 요약

| 전문가 | 건너뜀 조건 |
|--------|-----------|
| HOW-B 자료 리서처 | 추가 스킬 불필요 선택 시 |
| HOW-C 프론트엔드 | 단순 API 서비스 (화면 없음) |
| HOW-D 백엔드 | data_persistence 태그 없을 때 |
| HOW-E 데이터 엔지니어 | small_scale + data_persistence 없을 때 |
| HOW-F DB 설계자 | data_persistence 태그 없을 때 |
| HOW-G AI 엔지니어 | ai_none 또는 ai_later 태그일 때 |

---

## 총 질문 수 (태그 조합별)

| 시나리오 | 문항 수 |
|---------|--------|
| 풀 스택 + AI + 대규모 | ~35개 |
| 풀 스택 + AI 없음 | ~25개 |
| 단순 웹앱 (소규모) | ~18개 |
| API 서비스 (화면 없음) | ~12개 |
