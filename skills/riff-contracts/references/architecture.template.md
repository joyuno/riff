# Architecture Contract 템플릿

이 파일은 `references/architecture.template.md`이다.
병렬 에이전트 스폰 전 오케스트레이터가 직접 작성한다.

---

# [프로젝트명] — 아키텍처 계약서

```
생성 Pulse: N
작성자: 오케스트레이터
```

---

## 1. 에이전트 소유권 맵

소유 에이전트 외의 에이전트는 해당 영역을 읽기만 가능하다. 쓰려면 오케스트레이터 승인 필요.

| 에이전트 ID | 담당 디렉토리 | 쓰기 권한 |
|-----------|------------|---------|
| frontend-agent | `src/frontend/`, `public/` | 전용 |
| backend-agent | `src/backend/`, `src/api/` | 전용 |
| shared (오케스트레이터만) | `src/shared/`, `src/types/` | 오케스트레이터 승인 |

---

## 2. API 엔드포인트 소유권

계약서에 없는 엔드포인트를 에이전트가 임의로 추가하는 것은 금지한다.
추가가 필요하면 오케스트레이터에게 보고 후 이 계약서를 먼저 업데이트한다.

| 엔드포인트 | 메서드 | 소유 에이전트 | 소비 에이전트 | 상태 |
|-----------|--------|-------------|-------------|------|
| /api/auth/login | POST | backend-agent | frontend-agent | 확정 |
| /api/auth/refresh | POST | backend-agent | frontend-agent | 확정 |
| /api/users/{id} | GET | backend-agent | frontend-agent | 확정 |

> 상태: `확정` = 번복 불가 / `초안` = 변경 가능 / `보류` = 구현 제외

---

## 3. 기술 결정 (확정)

`확정`으로 표시된 결정은 에이전트가 번복할 수 없다.
변경이 필요하면 오케스트레이터에게 보고 후 이 계약서를 먼저 업데이트한다.

| 결정 사항 | 선택 | 금지된 대안 | 이유 |
|---------|------|-----------|------|
| 인증 방식 | JWT Bearer 토큰 | Session Cookie | 모바일/API 클라이언트 지원 |
| API 응답 형식 | `{ data, error }` 래핑 | 직접 반환 | 에러 처리 통일 |
| 상태 관리 | Zustand | Redux, Context | 번들 크기, 단순성 |
| 스타일 | Tailwind CSS | CSS Modules, styled-components | 디자인 토큰 일관성 |

---

## 4. 에이전트 간 협의 인터페이스

에이전트 A가 정의하고 에이전트 B가 소비하는 경계면 요약.
상세 shape은 `_workspace/contracts/{이름}-type.md` 참조.

| 인터페이스명 | 정의 에이전트 | 소비 에이전트 | 상세 계약서 |
|-----------|------------|------------|----------|
| UserProfile | backend-agent | frontend-agent | `contracts/user-type.md` |
| ProductItem | backend-agent | frontend-agent | `contracts/product-type.md` |

---

## 5. 에이전트별 준수 규칙

각 에이전트 프롬프트에 이 섹션을 그대로 붙여넣는다.

```
【Architecture Contract 준수 규칙】

읽기: _workspace/contracts/architecture.md

1. 소유권 맵의 내 영역 밖 파일은 수정 금지.
   수정이 필요하면 구현 중단 후 오케스트레이터에게 보고.

2. API 엔드포인트 표에 없는 엔드포인트 임의 생성 금지.
   새 엔드포인트가 필요하면 구현 중단 후 오케스트레이터에게 보고.

3. 기술 결정 표의 '확정' 항목 번복 금지.
   '금지된 대안'에 해당하는 것을 사용하지 말 것.

4. 인터페이스 표에 없는 새 공유 타입을 발명하지 말 것.
   필요하면 오케스트레이터에게 보고 후 Type Contract 먼저 작성.

5. 결과를 _workspace/pulse-N/{에이전트명}-result.md에 저장.
   대화로 결과 반환 금지.
```

---

## 6. 충돌 해결 우선순위

같은 인터페이스에 대해 두 에이전트가 다른 구현을 내놓았을 때:

1. Architecture Contract 정의 우선
2. Type Contract shape 우선
3. 먼저 완료된 에이전트 구현 우선
4. 모두 해당 없으면 → 오케스트레이터 판단

---

*이 파일은 `_workspace/contracts/architecture.md`에 복사 후 프로젝트에 맞게 수정한다.*
