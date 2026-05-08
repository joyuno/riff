# pulse-status.md 포맷 정의

이 파일은 `_workspace/pulse-status.md`의 형식을 정의한다.
오케스트레이터는 매 단계 진입/종료 시 이 파일을 갱신한다.
새 세션 시작 시 이 파일이 있으면 읽고 즉시 재개한다.

---

## 포맷

```markdown
# Pulse 실행 상태

## 현재 위치
- Pulse: [N]
- 단계: [ASK / EXPLORE / BUILD / VERIFY / LEARN]
- 하위 단계: [BUILD의 경우 PLAN / CONTRACT / EXECUTE]
- 최종 갱신: [YYYY-MM-DD HH:mm]

## 인터뷰 태그
[enriched-layers에서 수집된 태그 목록]
- [태그1]
- [태그2]

## 에이전트 상태
| 에이전트 | 상태 | 결과 파일 |
|---------|------|---------|
| [이름] | ⏳ 대기 / 🔄 진행 / ✅ 완료 / ❌ 실패 | [경로] |

## 자동화 체크리스트
- [ ] DNA 로드 (.pulse/user-dna/)
- [ ] 항체 주입 (.pulse/antibodies/ → active 항체 매칭)
- [ ] 계약서 확인 (_workspace/contracts/README.md)
- [ ] explore-synthesis.md 읽기 (존재하는 경우)
- [ ] master-plan.md 읽기 (존재하는 경우)

## 계약서 현황
| 계약서 | 유형 | 상태 |
|--------|------|------|
| [파일명] | [type/behavior/...] | 활성 / 초안 |

## 성공 기준 진행도
| 기준 | 상태 | 비고 |
|------|------|------|
| [success-criteria.md에서 가져옴] | ⏳ 미검증 / 🔄 부분 달성 / ✅ 달성 | [메모] |

## 되감기 이력
[없으면 "없음"]

## 질문 예산
- 레벨: [A/B/C/D]
- 확신도: [0-100%]
```

---

## 갱신 규칙

### 단계 진입 시 (필수)
1. "현재 위치" 업데이트
2. "자동화 체크리스트" 확인 — 미체크 항목 즉시 실행
3. "최종 갱신" 타임스탬프 갱신

### 단계 종료 시 (필수)
1. "에이전트 상태" 업데이트 (BUILD)
2. "계약서 현황" 업데이트 (BUILD > CONTRACT)
3. "성공 기준 진행도" 업데이트 (VERIFY)
4. "현재 위치"를 다음 단계로 이동

### 세션 시작 시 (필수)
1. `_workspace/pulse-status.md` 존재 확인
2. 있으면 읽고 "현재 위치"에서 즉시 재개
3. "자동화 체크리스트" 미체크 항목 실행 (DNA 로드, 항체 주입 등)
4. 없으면 Pulse 0부터 시작

### Pulse 완료 시
1. "현재 위치" Pulse 번호 +1
2. 이전 Pulse 에이전트 상태 초기화
3. LEARN 결과 반영

---

## 자동화 체크리스트 상세

### DNA 로드
- `.pulse/user-dna/preferences.md` 존재 시 읽기
- 커뮤니케이션 스타일, 코딩 선호 적용
- 체크 후: `- [x] DNA 로드`

### 항체 주입
- `.pulse/antibodies/` 스캔
- `status: active`이고 현재 작업과 관련된 항체 필터
- 에이전트 프롬프트에 체크리스트 포함
- 체크 후: `- [x] 항체 주입 (api-response-wrapping, auth-token-expiry)`

### 계약서 확인
- `_workspace/contracts/README.md` 읽기
- 이번 Pulse에서 필요한 계약서 목록 파악
- 체크 후: `- [x] 계약서 확인`

### explore-synthesis 읽기
- `_workspace/pulse-N/explore-synthesis.md` 존재 시 읽기
- BUILD 제약 조건 반영
- 체크 후: `- [x] explore-synthesis.md 읽기`
