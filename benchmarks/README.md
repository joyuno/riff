# Riff 벤치마크 — OMC Ground Truth 방식

Riff 플러그인의 4가지 핵심 능력을 자동 채점하는 벤치마크 스위트입니다.
OMC(oh-my-claudecode)의 harsh-critic 벤치마크 방식을 Riff 도메인에 맞게 포팅했습니다.

---

## 개요

### 평가 차원

| 차원 | 설명 | Fixture 수 |
|------|------|-----------|
| **인터뷰 품질** (interview) | 모호한 요청에 대해 핵심 의사결정 질문을 얼마나 잘 하는가 | 2 |
| **경계면 QA** (boundary) | API↔훅 shape 불일치, 라우팅 오류 등 경계면 버그를 찾는가 | 2 |
| **Live QA** (live-app) | 실제 앱 유저 저니에서 숨겨진 UI/UX 버그를 발견하는가 | 1 |
| **면역 시스템** (immunity) | 한 번 고친 버그 패턴이 다른 곳에서 반복될 때 사전 방지하는가 | 1 |

### 신규 시나리오 (v1.0 — depth·canvas)

Riff v1.0의 adaptive depth 판정과 Living CANVAS.md 재개 로직을 검증하는 시나리오입니다.
`must_have`/`must_not` 체크리스트 형식의 ground truth를 사용하며, 아직 `scoring/scorer.py`의
키워드 매칭 자동 채점 대상이 아닙니다 — 현재는 수동/정성 채점, 자동화는 후속 릴리스 범위입니다.

| 시나리오 | Fixture | Ground Truth | 판정 기준 |
|---|---|---|---|
| depth-ambiguous-notes | `fixtures/depth/ambiguous-brief-notes.md` | `ground-truth/depth-ambiguous-notes.json` | "메모 앱" 같은 모호 브리프에서 depth 판정 정답률(복잡 또는 가정 선언 노출)을 측정 |
| depth-ambiguous-tracker | `fixtures/depth/ambiguous-brief-tracker.md` | `ground-truth/depth-ambiguous-tracker.json` | "뚝딱" 같은 어휘에 낚이지 않고 성공 기준 부재 시 가정 선언을 강제하는지 측정 |
| canvas-mid-build-restart | `fixtures/canvas/mid-build-restart.md` | `ground-truth/canvas-restart.json` | BUILD 도중 dirty exit 후 재시작 정확도(canvas-lint 선실행 + 미완료 태스크부터 재개) 측정 |
| rewind-anchor | `fixtures/canvas/rewind-anchor.md` | `ground-truth/rewind-anchor.json` | PROVE 3회 연속 실패 시 커밋 앵커 기반 되감기가 증거 백업 선행·CANVAS 갱신·항체/`.riff/` 보존을 지키는지 측정 |

**speed-tax**(계획됨): medium 프로파일 사이클의 오버헤드 wall-clock 측정(목표 ≤15%) — 측정 스크립트는 후속 릴리스 범위.

### 핵심 설계 원칙

1. **Fixture**: 의도적 결함이 심어진 입력물 (모호한 요청, 버그 있는 코드, 시나리오)
2. **Ground Truth**: 각 결함에 대한 정답 JSON (키워드 + 심각도)
3. **Scorer**: 키워드 매칭 기반 자동 채점 (`scoring/scorer.py`)
4. **Runner**: 자동 실행 파이프라인 (`run-benchmark.sh`)

---

## 실행 방법

### 요구사항

```bash
# Python 3.9+
python --version

# Claude CLI (claude -p 명령어 필요)
claude --version

# ANTHROPIC_API_KEY 환경변수
export ANTHROPIC_API_KEY=sk-ant-...
```

### 기본 실행

```bash
cd /path/to/riff/benchmarks

# 전체 벤치마크 실행 (Riff 적용)
./run-benchmark.sh --with-riff

# 특정 차원만 실행
./run-benchmark.sh --dimension interview
./run-benchmark.sh --dimension boundary

# 특정 fixture만 실행
./run-benchmark.sh --fixture interview-ecommerce

# Riff 없이 실행 (baseline 측정)
./run-benchmark.sh --without-riff

# 양쪽 비교
./run-benchmark.sh --compare

# 베이스라인 저장
./run-benchmark.sh --with-riff --save-baseline
```

### 결과 확인

```bash
# 최신 결과 확인
cat results/report.md

# JSON 결과 확인
cat results/results.json

# 베이스라인 비교
./run-benchmark.sh --compare
```

---

## 채점 알고리즘

### 키워드 매칭

각 Ground Truth finding은 `keywords` 배열을 갖습니다. 에이전트 출력에서 해당 키워드가
몇 개나 등장하는지 세어 매칭 여부를 결정합니다.

```
기본 임계값: MIN_KEYWORD_MATCHES = 2
동적 임계값: 키워드가 6개 이상이면 40% 비례 (6개→3개, 10개→4개)
```

#### 텍스트 정규화

```
1. lowercase 변환
2. NFKC 유니코드 정규화 (한글 자모 분리 방지)
3. 구두점·분리자 → 공백 (` * _ # ( ) [ ] { } < > " ' . , ; ! ? | \ `)
4. 하이픈·슬래시·콜론 연속 → 공백
5. 연속 공백 → 단일 공백
```

#### 구(phrase) 폴백

멀티토큰 키워드(예: "동시 사용자")는 직접 포함 여부를 먼저 확인하고,
실패 시 모든 토큰이 순서 무관하게 존재하면 매칭으로 인정합니다.

### 심각도 인접성

`ALLOW_ADJACENT_SEVERITY = true` 설정 시:
- CRITICAL ↔ MAJOR: 허용
- MAJOR ↔ MINOR: 허용
- CRITICAL ↔ MINOR: 불허 (거리 2)

### 메트릭 계산

| 메트릭 | 계산 방법 | 가중치 |
|--------|----------|--------|
| `true_positive_rate` | 매칭된 GT / 전체 GT | 0.30 |
| `false_negative_penalty` | (1 - 놓친 GT / 전체 GT) | 0.25 |
| `spurious_penalty` | (1 - 불필요 findings / 전체 findings) | 0.15 |
| `coverage_bonus` | 차원별 커버리지 | 0.15 |
| `evidence_rate` | 증거 포함 비율 | 0.15 |

**Composite Score** = 위 메트릭의 가중 합산 (0~100점)

---

## 베이스라인 관리

### 베이스라인 저장

```bash
# Riff 적용 결과를 베이스라인으로 저장
./run-benchmark.sh --with-riff --save-baseline

# 저장 위치: baselines/baseline_YYYY-MM-DD.json
```

### 베이스라인 비교

```bash
./run-benchmark.sh --compare
# 결과에 delta 컬럼 추가: +/- 변화량, 회귀(±1% 이상 하락) 경고
```

### 회귀 감지 임계값

- 종합 점수 ±1% 이상 변화 시 경고 표시
- CRITICAL finding 놓친 경우 즉시 경고
- 차원별 점수도 개별 추적

---

## With-Riff vs Without-Riff 비교

`--compare` 모드는 동일 fixture를 두 가지 모드로 실행하고 head-to-head 비교를 생성합니다.

```
fixture: vague-ecommerce
  with-riff:    composite=82.3%  tp=90%  fn=10%
  without-riff: composite=41.5%  tp=35%  fn=65%
  delta:         +40.8%  ← Riff 효과
```

---

## 비용 예상

| 모드 | fixture 수 | 예상 토큰 | 예상 비용 |
|------|-----------|----------|---------|
| `--dimension interview` | 2 | ~8K | ~$0.05 |
| `--dimension boundary` | 2 | ~6K | ~$0.04 |
| `--with-riff` (전체) | 6 | ~30K | ~$0.20 |
| `--compare` (전체) | 6×2 | ~60K | ~$0.40 |

_claude-sonnet 기준. opus 사용 시 5× 비용 예상._

---

## 디렉토리 구조

```
benchmarks/
├── README.md                     # 이 파일
├── run-benchmark.sh              # 메인 실행 스크립트
├── scoring/
│   ├── scorer.py                 # 키워드 매칭 채점기
│   └── reporter.py               # 마크다운 보고서 생성기
├── fixtures/
│   ├── interview/                # 인터뷰 품질 측정
│   │   ├── vague-ecommerce.md    # 모호한 쇼핑몰 요청
│   │   └── vague-trading.md      # 모호한 퀀트 요청
│   ├── boundary/                 # 경계면 QA 측정
│   │   ├── api-shape-mismatch.md # API↔훅 shape 불일치
│   │   └── route-prefix-missing.md
│   ├── live-app/                 # Live QA 측정
│   │   └── order-dashboard.md    # 주문 대시보드 유저 저니
│   ├── immunity/                 # 면역 시스템 측정
│   │   └── repeated-unwrap-bug.md
│   ├── depth/                    # v1.0: adaptive depth 판정 측정
│   │   ├── ambiguous-brief-notes.md
│   │   └── ambiguous-brief-tracker.md
│   └── canvas/                   # v1.0: Living CANVAS.md 재개 로직 측정
│       ├── mid-build-restart.md
│       └── rewind-anchor.md      # 커밋 앵커 기반 되감기 측정
├── ground-truth/
│   ├── interview-ecommerce.json
│   ├── interview-trading.json
│   ├── boundary-api-shape.json
│   ├── boundary-route-prefix.json
│   ├── live-order-dashboard.json
│   ├── immunity-unwrap.json
│   ├── depth-ambiguous-notes.json
│   ├── depth-ambiguous-tracker.json
│   ├── canvas-restart.json
│   └── rewind-anchor.json
├── baselines/                    # 저장된 베이스라인 결과
└── results/                      # 벤치마크 실행 결과
```

---

## Ground Truth 기여 가이드

새 fixture를 추가하려면:

1. `fixtures/{dimension}/` 에 `.md` 파일 작성 — 의도적 결함 포함
2. `ground-truth/{fixture-id}.json` 작성 — 각 결함의 키워드와 심각도 정의
3. `./run-benchmark.sh --fixture {fixture-id} --dry-run` 으로 파이프라인 검증
4. 실제 실행 후 scorer 출력으로 ground truth 키워드 조정

### Ground Truth finding 작성 원칙

- `keywords`는 6~8개 권장 (너무 적으면 false positive, 너무 많으면 false negative)
- 한국어·영어 혼용 가능 (정규화가 양쪽 처리)
- `explanation`은 "왜 이것이 문제인가"를 서술 (채점에 사용되지 않지만 문서화 목적)
- `location`은 파일:섹션 형식으로 가능하면 명시
