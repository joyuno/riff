# 답변→아키텍처 매핑 테이블

인터뷰 답변 조합을 구체적인 아키텍처 결정으로 변환하는 매핑 테이블입니다. 스코어카드에서 "즉시 진행 가능" 판정을 받은 후 이 테이블을 적용합니다.

---

## 1. 시스템 아키텍처 매핑

### 입력 변수
- `scale`: Q5 답변 (A=소형/B=중형/C=대형)
- `timeline`: Q7 답변 (A=2주/B=1-2개월/C=3개월+)
- `tags`: Q1에서 추출된 태그 목록

### 매핑 테이블

| scale | tags | 추천 아키텍처 | 이유 |
|---|---|---|---|
| A (소형) | 없음 | 모놀리식 단일 서버 | 복잡도 최소화, 운영 단순 |
| A (소형) | `reliability_critical` | 모놀리식 + 자동 백업 | 소규모지만 신뢰성 필요 |
| B (중형) | 없음 | 모놀리식 + CDN | 표준 웹 서비스 구조 |
| B (중형) | `performance_critical` | 모놀리식 + 캐싱 레이어 | 속도 최적화, 복잡도 최소 |
| B (중형) | `reliability_critical` | 모놀리식 + DB 복제 | 고가용성 단순 구현 |
| C (대형) | 없음 | 수평 확장 모놀리식 | 마이크로서비스 전 단계 |
| C (대형) | `performance_critical` | 마이크로서비스 + 비동기 큐 | 독립 확장 필요 |
| C (대형) | `market_risk` | 서버리스 + 관리형 서비스 | 빠른 피벗 + 자동 확장 |
| C (대형) | `compliance_required` | 자체 인프라 + 감사 레이어 | 데이터 통제권 필요 |

### 특수 조합

| 조합 | 결정 |
|---|---|
| scale=A + timeline=A (급함+소형) | SQLite + 단일 프로세스 + Railway/Render 즉시 배포 |
| scale=C + timeline=A (급함+대형) | 서버리스 우선 (Lambda/Vercel) + 관리형 DB + 나중에 마이그레이션 |
| `compliance_required` + 어떤 규모든 | 온프레미스 또는 단일 리전 클라우드, 암호화 필수, 감사 로그 필수 |

---

## 2. 데이터베이스 매핑

### 입력 변수
- `data_type`: Q6 기능 목록에서 추론 (관계형 데이터 vs 문서 vs 시계열 등)
- `scale`: Q5 답변
- `tech_stack`: Q8 답변

### 매핑 테이블

| 데이터 특성 | scale | 추천 DB | 대안 |
|---|---|---|---|
| 관계형, 트랜잭션 중요 | A/B | PostgreSQL | MySQL, SQLite (A만) |
| 관계형, 트랜잭션 중요 | C | PostgreSQL + Read Replica | Aurora |
| 문서 중심, 유연한 스키마 | A/B | MongoDB | Firestore |
| 문서 중심, 빠른 출시 | B/C | Supabase (PostgreSQL 관리형) | PlanetScale |
| 실시간 동기화 필요 | 모든 규모 | Firebase Realtime / Supabase Realtime | — |
| 시계열 데이터 (로그, 메트릭) | B/C | TimescaleDB 또는 InfluxDB | — |
| 전문 검색 필요 | B/C | PostgreSQL + pgvector 또는 Elasticsearch | Meilisearch |
| AI/벡터 검색 필요 | 모든 규모 | pgvector (소형) / Pinecone (대형) | Chroma, Weaviate |

### 관리형 우선 기준
- `timeline=A` → 반드시 관리형 DB 사용 (설정 시간 없음)
- `market_risk` 태그 → 관리형 우선 (피벗 용이)
- `compliance_required` 태그 → 자체 운영 또는 규정 준수 인증 완료 관리형만

---

## 3. 배포/인프라 매핑

### 입력 변수
- `tech_stack`: Q8 답변
- `scale`: Q5 답변
- `timeline`: Q7 답변
- `tags`: Q1 태그

### 매핑 테이블

| tech_stack | scale | timeline | 추천 배포 환경 |
|---|---|---|---|
| Next.js / React | A/B | A/B | Vercel (제로 설정) |
| Next.js / React | C | B/C | Vercel Enterprise 또는 AWS ECS |
| Python / FastAPI | A/B | A/B | Railway 또는 Render |
| Python / FastAPI | C | B/C | AWS ECS / GCP Cloud Run |
| Node.js / Express | A/B | A | Railway |
| Node.js / Express | C | B/C | AWS ECS 또는 Kubernetes |
| 미정 | A | A | Railway (범용, 빠름) |
| 미정 | C | A | Vercel 서버리스 함수 + Supabase |

### 컨테이너화 기준
- scale=A: 선택 (Docker 사용 시 이식성 향상)
- scale=B: 권장 (Docker Compose 또는 단일 컨테이너)
- scale=C: 필수 (Docker + 오케스트레이션)

---

## 4. 에이전트 팀 구성 매핑

Riff 에이전트 팀의 수와 구성을 결정합니다.

### 입력 변수
- `timeline`: Q7 답변
- `scale`: Q5 답변
- `tags`: Q1 태그
- `feature_count`: Q6의 "반드시" 항목 수

### 에이전트 수 결정

| timeline | scale | feature_count | 에이전트 수 | 병렬화 수준 |
|---|---|---|---|---|
| A (2주) | A | 1-2개 | 3-4개 | 최대 병렬 |
| A (2주) | B | 2-3개 | 5-7개 | 최대 병렬 |
| A (2주) | C | 3개 | 8-10개 | 최대 병렬 |
| B (1-2개월) | A/B | 2-3개 | 4-6개 | 표준 병렬 |
| B (1-2개월) | C | 3개 | 7-9개 | 표준 병렬 |
| C (3개월+) | 모든 규모 | 모든 수 | 5-8개 | 품질 우선 |

### 에이전트 역할 구성 패턴

**패턴 A: 속도 최우선 (timeline=A)**
```
- 구현 에이전트 × 3 (병렬, 기능별 분담)
- QA 에이전트 × 1 (기본 검증만)
- 통합 에이전트 × 1 (최종 조립)
```

**패턴 B: 균형 (timeline=B)**
```
- 구현 에이전트 × 2
- 테스트 에이전트 × 1
- 문서 에이전트 × 1
- 리뷰 에이전트 × 1
```

**패턴 C: 품질 우선 (timeline=C 또는 compliance_required)**
```
- 구현 에이전트 × 2
- 테스트 에이전트 × 2 (단위/통합)
- 보안 에이전트 × 1
- 문서 에이전트 × 1
- 리뷰 에이전트 × 1
```

**태그별 전문 에이전트 추가:**
- `performance_critical` → 성능 테스트 에이전트 추가
- `reliability_critical` → 장애 시나리오 테스트 에이전트 추가
- `compliance_required` → 보안 감사 에이전트 추가

---

## 5. QA 전략 매핑

### Tier 정의

| Tier | 적용 기준 | 포함 내용 |
|---|---|---|
| Tier 1 (기본) | timeline=A, scale=A, 내부 도구 | 핵심 기능 스모크 테스트, 수동 검증 |
| Tier 2 (표준) | timeline=B, scale=B | 단위 테스트 70%+, 통합 테스트 핵심 경로, 스테이징 환경 |
| Tier 3 (강화) | timeline=C, scale=C | 단위 90%+, 통합 전체, E2E 핵심 시나리오, 성능 테스트, 보안 스캔 |
| Tier 4 (엔터프라이즈) | compliance_required, 금융/의료 | Tier 3 + 규정 준수 감사, 침투 테스트, 재해 복구 테스트 |

### QA Tier 결정 로직

```
compliance_required 태그 → Tier 4 (무조건)
scale=C + reliability_critical → Tier 3
timeline=C → Tier 3
scale=B + timeline=B → Tier 2
scale=A 또는 timeline=A → Tier 1
(복수 조건 시 높은 Tier 적용)
```

---

## 6. 예상 Riff 수 계산

### 공식

```
기본 Riff = feature_count (Q6 반드시 항목 수) × 3
              + feature_count (Q6 있으면 좋음) × 1

조정:
+ timeline=A: × 1.5 (병렬화로 증가)
+ scale=C: + 3 (인프라/스케일링 Riff 추가)
+ reliability_critical: + 2 (테스트/검증 Riff 추가)
+ compliance_required: + 4 (보안/감사 Riff 추가)
+ domain 전문가 질문 완료: + 2 (도메인 특화 Riff 추가)
```

### 예시 계산

**시나리오: 스마트스토어 자동화, 반드시 3개, 있으면 좋음 2개, 1-2개월, B규모**
```
기본 = 3×3 + 2×1 = 11
timeline=B → 조정 없음
scale=B → 조정 없음
도메인 완료 → +2
합계: 13 Riff
```

**시나리오: 퀀트 트레이딩, 반드시 2개, 2주, A규모, reliability_critical**
```
기본 = 2×3 = 6
timeline=A → ×1.5 = 9
reliability_critical → +2 = 11
합계: 11 Riff
```

---

## 7. 최종 아키텍처 결정 출력 형식

```markdown
## 아키텍처 결정 요약

**인터뷰 기반 입력:**
- scale: B (100~1,000명)
- timeline: B (1~2개월)
- tags: reliability_critical, market_risk
- feature_count: 반드시 3개, 있으면 좋음 2개

**결정:**

| 항목 | 결정 | 근거 |
|---|---|---|
| 시스템 구조 | 모놀리식 + DB 복제 | scale=B + reliability_critical |
| 데이터베이스 | Supabase (PostgreSQL 관리형) | timeline=B + market_risk |
| 배포 환경 | Railway (초기) → AWS 이전 준비 | scale=B, 이후 C 대비 |
| 에이전트 수 | 6개, 표준 병렬 | timeline=B + scale=B + feature=3 |
| QA Tier | Tier 2 | timeline=B + scale=B |
| 예상 Riff 수 | 13개 | 계산식 적용 |

**핵심 트레이드오프:**
1. Supabase 사용 → 초기 속도 UP, 장기 비용 UP (월 $25~$500)
2. 모놀리식 선택 → 운영 단순, 특정 기능 독립 확장 불가
3. Railway 시작 → 즉시 배포 가능, 10,000명 초과 시 마이그레이션 필요

**가정 (확인 필요):**
- [ ] 동시 사용자 피크가 총 사용자의 20% 미만이라고 가정
- [ ] 데이터 보존 기간 1년으로 가정 (규정 요구사항 미확인)
```
