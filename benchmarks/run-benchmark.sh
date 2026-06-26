#!/usr/bin/env bash
# =============================================================================
# Riff Benchmark Runner
# OMC Ground Truth 방식 기반의 자동 채점 벤치마크 실행 스크립트
#
# 사용법:
#   ./run-benchmark.sh                         # 전체 실행 (with-riff)
#   ./run-benchmark.sh --dimension interview   # 특정 차원만
#   ./run-benchmark.sh --fixture interview-ecommerce  # 특정 fixture만
#   ./run-benchmark.sh --with-riff            # Riff 적용 실행
#   ./run-benchmark.sh --without-riff         # 기본 실행 (baseline 측정)
#   ./run-benchmark.sh --compare               # 양쪽 비교
#   ./run-benchmark.sh --save-baseline         # 베이스라인 저장
#   ./run-benchmark.sh --dry-run               # 파이프라인 검증만 (API 호출 없음)
# =============================================================================

set -euo pipefail

# ============================================================
# 디렉토리 설정
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"
GROUND_TRUTH_DIR="${SCRIPT_DIR}/ground-truth"
RESULTS_DIR="${SCRIPT_DIR}/results"
BASELINES_DIR="${SCRIPT_DIR}/baselines"
SCORING_DIR="${SCRIPT_DIR}/scoring"

TIMESTAMP="$(date +%Y-%m-%dT%H-%M-%S)"

# ============================================================
# 색상 출력
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
header()  { echo -e "\n${BOLD}=== $* ===${RESET}\n"; }

# ============================================================
# 기본값
# ============================================================

MODE="with-riff"         # with-riff | without-riff | compare
DIMENSION=""              # 비어있으면 전체
FIXTURE_FILTER=""         # 비어있으면 전체
SAVE_BASELINE=false
DRY_RUN=false
MODEL="${RIFF_MODEL:-claude-sonnet-4-5}"

# ============================================================
# 인자 파싱
# ============================================================

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-riff)
      MODE="with-riff"
      shift
      ;;
    --without-riff)
      MODE="without-riff"
      shift
      ;;
    --compare)
      MODE="compare"
      shift
      ;;
    --dimension)
      DIMENSION="$2"
      shift 2
      ;;
    --fixture)
      FIXTURE_FILTER="$2"
      shift 2
      ;;
    --save-baseline)
      SAVE_BASELINE=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --help|-h)
      grep "^# " "$0" | head -20 | sed 's/^# //'
      exit 0
      ;;
    *)
      error "알 수 없는 인자: $1"
      exit 1
      ;;
  esac
done

# ============================================================
# 사전 검증
# ============================================================

header "Riff 벤치마크 시작"

# API 키 확인 (dry-run 제외)
if [[ "${DRY_RUN}" == false ]]; then
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    error "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."
    echo "  export ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
  fi
fi

# claude CLI 확인
if [[ "${DRY_RUN}" == false ]]; then
  if ! command -v claude &>/dev/null; then
    error "claude CLI를 찾을 수 없습니다."
    echo "  설치: npm install -g @anthropic-ai/claude-code"
    exit 1
  fi
fi

# Python 확인 (python3 우선, 없으면 python 폴백 — Windows/일부 환경 호환).
# Windows의 Microsoft Store python 별칭 스텁은 import 검사에서 걸러진다.
PYTHON=""
for _cand in python3 python py; do
  if command -v "${_cand}" &>/dev/null && "${_cand}" -c "import sys; sys.exit(0 if sys.version_info[0]==3 else 1)" &>/dev/null; then
    PYTHON="${_cand}"; break
  fi
done
if [[ -z "${PYTHON}" ]]; then
  error "Python 3을 찾을 수 없습니다 (python3 또는 python)."
  exit 1
fi

# 디렉토리 확인
for dir in "${FIXTURES_DIR}" "${GROUND_TRUTH_DIR}" "${SCORING_DIR}"; do
  if [[ ! -d "${dir}" ]]; then
    error "디렉토리를 찾을 수 없습니다: ${dir}"
    exit 1
  fi
done

mkdir -p "${RESULTS_DIR}" "${BASELINES_DIR}"

info "모드: ${MODE}"
info "모델: ${MODEL}"
[[ -n "${DIMENSION}" ]] && info "차원: ${DIMENSION}"
[[ -n "${FIXTURE_FILTER}" ]] && info "Fixture: ${FIXTURE_FILTER}"

# ============================================================
# Fixture 목록 수집
# ============================================================

collect_fixtures() {
  local dimension="${1:-}"
  local fixture_filter="${2:-}"
  local fixtures=()

  local dims
  if [[ -n "${dimension}" ]]; then
    case "${dimension}" in
      interview) dims=("interview") ;;
      boundary)  dims=("boundary") ;;
      live-app)  dims=("live-app") ;;
      memory)  dims=("memory") ;;
      *)
        error "알 수 없는 차원: ${dimension}"
        echo "  유효한 차원: interview, boundary, live-app, memory"
        exit 1
        ;;
    esac
  else
    dims=("interview" "boundary" "live-app" "memory")
  fi

  for dim in "${dims[@]}"; do
    local dim_dir="${FIXTURES_DIR}/${dim}"
    [[ -d "${dim_dir}" ]] || continue
    while IFS= read -r -d '' file; do
      local basename
      basename="$(basename "${file}" .md)"
      if [[ -n "${fixture_filter}" && "${basename}" != "${fixture_filter}" ]]; then
        continue
      fi
      # ground-truth 파일이 있는 경우에만 포함
      local gt_file
      gt_file="$(find_ground_truth "${basename}")"
      if [[ -n "${gt_file}" ]]; then
        fixtures+=("${dim}:${basename}:${file}")
      else
        warn "Ground truth 없음, 스킵: ${basename}"
      fi
    done < <(find "${dim_dir}" -name "*.md" -print0 | sort -z)
  done

  printf '%s\n' "${fixtures[@]}"
}

find_ground_truth() {
  local fixture_id="$1"
  # ground-truth/{fixture_id}.json 또는 ground-truth/{dimension}-{name}.json
  local candidates=(
    "${GROUND_TRUTH_DIR}/${fixture_id}.json"
  )
  for c in "${candidates[@]}"; do
    [[ -f "${c}" ]] && echo "${c}" && return
  done
  echo ""
}

# ============================================================
# 단일 Fixture 실행
# ============================================================

run_fixture() {
  local mode="$1"
  local dim="$2"
  local fixture_id="$3"
  local fixture_path="$4"
  local output_dir="$5"

  local output_file="${output_dir}/${fixture_id}.txt"

  if [[ "${DRY_RUN}" == true ]]; then
    info "  [dry-run] ${fixture_id} — 스킵"
    echo "[dry-run placeholder output]" > "${output_file}"
    return 0
  fi

  # Fixture 내용 읽기
  local fixture_content
  fixture_content="$(cat "${fixture_path}")"

  # 시스템 프롬프트 구성
  local system_prompt
  if [[ "${mode}" == "with-riff" ]]; then
    system_prompt="$(build_riff_system_prompt "${dim}")"
  else
    system_prompt="$(build_baseline_system_prompt "${dim}")"
  fi

  # 사용자 메시지 구성
  local user_message
  user_message="$(build_user_message "${dim}" "${fixture_content}")"

  info "  실행 중: ${fixture_id} (${mode})..."
  local start_time
  start_time="$(date +%s)"

  # claude -p 호출
  local response
  if response="$(echo "${user_message}" | claude -p "${system_prompt}" 2>&1)"; then
    local end_time elapsed
    end_time="$(date +%s)"
    elapsed=$((end_time - start_time))
    echo "${response}" > "${output_file}"
    success "  완료: ${fixture_id} (${elapsed}s)"
  else
    local end_time elapsed
    end_time="$(date +%s)"
    elapsed=$((end_time - start_time))
    error "  실패: ${fixture_id} (${elapsed}s)"
    echo "ERROR: Claude API 호출 실패" > "${output_file}"
    return 1
  fi
}

# ============================================================
# 시스템 프롬프트 빌더
# ============================================================

build_riff_system_prompt() {
  local dim="$1"
  case "${dim}" in
    interview)
      cat <<'PROMPT'
당신은 Riff — 소프트웨어 프로젝트의 품질 게이트 에이전트입니다.

모호하거나 불완전한 요청을 받았을 때, 개발을 시작하기 전에 반드시 확인해야 할
핵심 의사결정 질문들을 체계적으로 도출합니다.

인터뷰 원칙:
- WHY (목적): 왜 만드는가? 어떤 문제를 해결하는가?
- WHO (사용자): 누가 사용하는가? 얼마나 많이?
- WHAT (기능): 무엇을 만드는가? MVP 범위는?
- HOW (기술): 어떻게 만드는가? 제약조건은?
- MEASURE (성공): 어떻게 성공을 측정하는가?

각 질문에는:
1. 질문 자체
2. 이 질문이 중요한 이유 (어떤 아키텍처 결정에 영향을 미치는가)
3. 가능한 답변 시나리오와 그에 따른 영향

을 포함하세요.
PROMPT
      ;;
    boundary)
      cat <<'PROMPT'
당신은 Riff — 소프트웨어 프로젝트의 품질 게이트 에이전트입니다.

코드 경계면(API↔훅, 라우트↔컴포넌트, DB↔서비스 레이어)에서 발생하는
버그를 탐지하는 것이 전문입니다.

분석 시:
- **CRITICAL**: 런타임 크래시, 데이터 손실, 보안 취약점
- **MAJOR**: 기능 오작동, 사용자 영향 있는 버그
- **MINOR**: 코드 품질, 잠재적 문제

각 버그에 대해:
1. 어느 파일의 어느 부분이 문제인가
2. 실제 어떤 오류가 발생하는가
3. 수정 방법

을 명시하세요.
PROMPT
      ;;
    live-app)
      cat <<'PROMPT'
당신은 Riff — 소프트웨어 프로젝트의 품질 게이트 에이전트입니다.

실제 동작하는 앱의 유저 저니를 분석하여 사용자가 마주칠 수 있는
UI/UX 버그와 데이터 정합성 문제를 찾습니다.

분석 관점:
- 상태 관리: 로딩/에러/성공 상태 처리
- 데이터 동기화: 낙관적 업데이트, 캐시 무효화
- 반응형: 모바일/데스크탑 뷰포트
- 접근성: 스크린 리더, 색맹, 키보드 네비게이션
- 에러 처리: 사용자에게 의미 있는 에러 메시지
PROMPT
      ;;
    memory)
      cat <<'PROMPT'
당신은 Riff — 소프트웨어 프로젝트의 품질 게이트 에이전트입니다.

면역 시스템 모드: 이전 대화에서 발견하고 수정한 버그 패턴을 기억하여,
동일한 패턴이 다른 곳에서 반복될 때 사전에 방지합니다.

분석 시:
1. 이전 수정 이력에서 버그 패턴을 추출
2. 현재 코드에서 동일 패턴 탐지
3. 재발 여부를 명시하고 올바른 패턴으로 수정

항체가 생성되었다면: "이 패턴은 [이전 수정]에서 확인된 버그 패턴입니다"라고
명시적으로 언급하세요.
PROMPT
      ;;
    *)
      echo "You are Riff, a software quality gate agent."
      ;;
  esac
}

build_baseline_system_prompt() {
  local dim="$1"
  case "${dim}" in
    interview)
      echo "You are a helpful software development assistant. Answer the user's questions about software development."
      ;;
    boundary)
      echo "You are a helpful code reviewer. Review the provided code and identify any issues."
      ;;
    live-app)
      echo "You are a helpful QA analyst. Review the provided user journey and identify any issues."
      ;;
    memory)
      echo "You are a helpful code reviewer. Review the provided code and identify any issues."
      ;;
    *)
      echo "You are a helpful assistant."
      ;;
  esac
}

build_user_message() {
  local dim="$1"
  local fixture_content="$2"

  case "${dim}" in
    interview)
      cat <<MSG
다음 사용자 요청을 받았습니다. 개발을 시작하기 전에 반드시 확인해야 할
핵심 질문들을 도출해주세요.

---
${fixture_content}
MSG
      ;;
    boundary)
      cat <<MSG
다음 코드에서 경계면 버그를 찾아주세요. API와 클라이언트 코드 사이의
shape 불일치, 타입 오류, 경로 오류에 집중하세요.

---
${fixture_content}
MSG
      ;;
    live-app)
      cat <<MSG
다음 애플리케이션의 유저 저니 시나리오를 검토하고,
사용자가 실제로 마주칠 수 있는 버그와 UX 문제를 찾아주세요.

---
${fixture_content}
MSG
      ;;
    memory)
      cat <<MSG
다음 대화 히스토리와 새 코드를 검토하세요.
이전에 수정한 버그 패턴이 새 코드에서 반복되고 있는지 확인하세요.

---
${fixture_content}
MSG
      ;;
    *)
      echo "${fixture_content}"
      ;;
  esac
}

# ============================================================
# 단일 모드 실행
# ============================================================

run_mode() {
  local mode="$1"
  local output_subdir="${RESULTS_DIR}/agent-output-${mode}-${TIMESTAMP}"
  mkdir -p "${output_subdir}"

  header "Fixture 실행: ${mode}"

  # Fixture 목록 수집
  local fixture_list
  mapfile -t fixture_list < <(collect_fixtures "${DIMENSION}" "${FIXTURE_FILTER}")

  if [[ ${#fixture_list[@]} -eq 0 ]]; then
    error "실행할 fixture가 없습니다."
    exit 1
  fi

  info "총 ${#fixture_list[@]}개 fixture 실행 예정"
  echo ""

  local failed=0
  for entry in "${fixture_list[@]}"; do
    IFS=':' read -r dim fixture_id fixture_path <<< "${entry}"
    run_fixture "${mode}" "${dim}" "${fixture_id}" "${fixture_path}" "${output_subdir}" || ((failed++)) || true
  done

  if [[ ${failed} -gt 0 ]]; then
    warn "${failed}개 fixture 실행 실패"
  fi

  # 채점
  header "채점: ${mode}"

  local score_output="${RESULTS_DIR}/scores-${mode}-${TIMESTAMP}.json"
  local report_output="${RESULTS_DIR}/report-${mode}-${TIMESTAMP}.md"

  local scorer_args=(
    "${PYTHON}" "${SCORING_DIR}/scorer.py"
    --ground-truth "${GROUND_TRUTH_DIR}"
    --results-dir "${output_subdir}"
    --output "${score_output}"
  )

  [[ -n "${FIXTURE_FILTER}" ]] && scorer_args+=(--fixture "${FIXTURE_FILTER}")

  if "${scorer_args[@]}"; then
    success "채점 완료: ${score_output}"
  else
    error "채점 실패"
    exit 1
  fi

  # 보고서 생성
  "${PYTHON}" "${SCORING_DIR}/reporter.py" \
    --input "${score_output}" \
    --output "${report_output}"
  success "보고서 생성: ${report_output}"

  # latest 심볼릭 링크 업데이트
  ln -sf "${score_output}" "${RESULTS_DIR}/scores-${mode}-latest.json"
  ln -sf "${report_output}" "${RESULTS_DIR}/report-${mode}-latest.md"

  echo ""
  cat "${report_output}"

  echo "${score_output}"
}

# ============================================================
# 베이스라인 저장
# ============================================================

save_baseline() {
  local score_file="$1"
  local baseline_file="${BASELINES_DIR}/baseline_${TIMESTAMP}.json"
  cp "${score_file}" "${baseline_file}"
  ln -sf "${baseline_file}" "${BASELINES_DIR}/baseline-latest.json"
  success "베이스라인 저장: ${baseline_file}"
}

# ============================================================
# 메인
# ============================================================

main() {
  case "${MODE}" in
    with-riff)
      score_file="$(run_mode "with-riff")"
      if [[ "${SAVE_BASELINE}" == true ]]; then
        save_baseline "${score_file}"
      fi
      ;;

    without-riff)
      score_file="$(run_mode "without-riff")"
      if [[ "${SAVE_BASELINE}" == true ]]; then
        save_baseline "${score_file}"
      fi
      ;;

    compare)
      header "비교 모드: With-Riff vs Without-Riff"

      wp_score="$(run_mode "with-riff")"
      wop_score="$(run_mode "without-riff")"

      comparison_output="${RESULTS_DIR}/comparison-${TIMESTAMP}.md"
      "${PYTHON}" "${SCORING_DIR}/reporter.py" \
        --compare "${wp_score}" "${wop_score}" \
        --output "${comparison_output}"

      success "비교 보고서: ${comparison_output}"
      echo ""
      cat "${comparison_output}"

      if [[ "${SAVE_BASELINE}" == true ]]; then
        save_baseline "${wp_score}"
      fi
      ;;

    *)
      error "알 수 없는 모드: ${MODE}"
      exit 1
      ;;
  esac

  header "완료"
  success "결과 디렉토리: ${RESULTS_DIR}"
}

main
