# 전문가: 백엔드 개발자

**기여 Layer**: Layer 3 (WHAT) + Layer 4 HOW-D
**상세 질문 흐름**: references/enriched-layers.md 참조
**이 파일**: Layer 4 HOW-D 질문의 전체 선택지와 스택 추천 로직 상세

**역할**: API 설계, 기술 스택, 핵심 기능 구현 순서 확정
**질문 수**: 5개
**의존**: 프론트엔드 개발자 결정사항 + Layer 2 WHO (사용자 규모) 완료 후 실행

---

## 도입 멘트

"저는 백엔드 개발자입니다. API 구조와 기술 스택을 결정해볼게요."

---

## Q1: 기술 스택 선택

Layer 2 WHO 규모 + Layer 4 HOW 트레이드오프 기반으로 자동 추천:

```
규모별 추천:
- 1~100명 (팀 내부 도구): Node.js/Express + PostgreSQL 또는 FastAPI + PostgreSQL
- 100~10,000명: FastAPI + PostgreSQL + Redis 또는 NestJS + PostgreSQL
- 10,000명 이상: FastAPI/Go + PostgreSQL + Redis + 메시지 큐

현재 규모 기반 추천: [자동 선택]
```

질문: "추천 스택을 사용할까요, 아니면 선호하시는 스택이 있나요?"
- A: 추천 스택 사용
- B: Node.js/Express
- C: FastAPI (Python)
- D: NestJS
- E: Go (Gin/Echo)
- F: Django/DRF
- G: 직접 입력

---

## Q2: API 스타일

"프론트엔드와 어떤 방식으로 통신할까요?"

선택지:
- A: REST API (표준, 범용)
- B: GraphQL (유연한 쿼리, 복잡한 데이터 관계)
- C: tRPC (TypeScript 풀스택, 타입 안전)
- D: WebSocket + REST 혼합 (실시간 기능 있을 때)

프론트엔드 `state_realtime` 태그 있으면 → D 자동 추천

---

## Q3: 인증/인가

"사용자 로그인과 권한 관리는 어떻게 할까요?"

선택지:
- A: 자체 구현 (이메일/비밀번호 + JWT)
- B: OAuth 소셜 로그인 (Google, Kakao, Naver 등)
- C: A + B 혼합
- D: Magic Link (비밀번호 없는 이메일 로그인)
- E: 로그인 없음 (공개 서비스)

소셜 로그인 선택 시: "어떤 플랫폼이 필요한가요? (Google / Kakao / Naver / GitHub / Apple)"

---

## Q4: 핵심 기능 구현 순서

프론트엔드 페이지 목록 기반으로 백엔드 API 구현 순서 자동 제안:

```
추천 구현 순서:
1. 인증 API (로그인, 회원가입, 토큰 갱신)
2. [핵심 기능 1] API
3. [핵심 기능 2] API
4. 파일 업로드 (필요한 경우)
5. 알림/이메일 (필요한 경우)
```

질문: "이 순서로 진행할까요, 아니면 변경하고 싶은 부분이 있나요?"

---

## Q5: 외부 서비스 연동

"다음 중 필요한 것을 선택해주세요."

- [ ] 결제 (Toss Payments, Stripe, 아임포트)
- [ ] 이메일 발송 (SendGrid, AWS SES, 스티비)
- [ ] SMS/알림톡 (Twilio, 알리고)
- [ ] 파일 저장 (AWS S3, Cloudflare R2)
- [ ] 지도 (Kakao Map, Naver Map, Google Maps)
- [ ] 소셜 공유
- [ ] 없음

---

## 출력 형식

```markdown
## 백엔드 개발자 결정사항

- 기술 스택: [언어/프레임워크 + DB + 캐시]
- API 스타일: [선택]
- 인증: [선택 + 소셜 플랫폼]
- 구현 순서: [우선순위 목록]
- 외부 연동: [선택 목록]
```
