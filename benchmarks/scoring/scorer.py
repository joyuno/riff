#!/usr/bin/env python3
"""
Riff Benchmark Scorer
OMC harsh-critic scorer.ts를 Python으로 포팅한 키워드 매칭 채점기.

사용법:
  python scorer.py --ground-truth ../ground-truth/ --results-dir ../results/agent-output/ --output ../results/output.json
  python scorer.py --ground-truth ../ground-truth/ --fixture interview-ecommerce --agent-output response.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================
# 상수
# ============================================================

MIN_KEYWORD_MATCHES = 2
ALLOW_ADJACENT_SEVERITY = True
SEVERITY_ORDER = ["CRITICAL", "MAJOR", "MINOR"]

# 가중치 (합계 = 1.0)
WEIGHTS = {
    "true_positive_rate":    0.30,
    "false_negative_penalty": 0.25,  # inverted: (1 - fnr)
    "spurious_penalty":      0.15,  # inverted: (1 - spur)
    "coverage_bonus":        0.15,
    "evidence_rate":         0.15,
}


# ============================================================
# 텍스트 정규화
# ============================================================

def normalize_text(value: str) -> str:
    """
    에이전트 출력과 키워드를 비교하기 위한 정규화.
    1. lowercase
    2. NFKC 유니코드 정규화 (한글 자모 분리 방지)
    3. 구두점·분리자 → 공백
    4. 하이픈·슬래시·콜론 연속 → 공백
    5. 연속 공백 → 단일 공백
    """
    text = value.lower()
    text = unicodedata.normalize("NFKC", text)
    # 구두점 제거
    text = re.sub(r'[`*_#()\[\]{}<>"\'.,;!?|\\]', " ", text)
    # 하이픈·슬래시·콜론 → 공백
    text = re.sub(r"[-/:]+", " ", text)
    # 연속 공백 정리
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================
# 키워드 매칭
# ============================================================

def keyword_matches_text(text: str, keyword: str) -> bool:
    """
    텍스트에서 키워드 매칭 여부 확인.
    1. 직접 포함 확인 (대소문자 무시)
    2. 정규화 후 포함 확인
    3. 멀티토큰 구(phrase) 폴백: 모든 토큰이 정규화 텍스트에 존재
    """
    lower_text = text.lower()
    lower_kw = keyword.lower()

    # 1. 직접 포함
    if lower_kw in lower_text:
        return True

    # 2. 정규화 후 포함
    norm_text = normalize_text(text)
    norm_kw = normalize_text(keyword)
    if not norm_kw:
        return False

    if norm_kw in norm_text:
        return True

    # 3. 구 폴백: 멀티토큰 키워드의 모든 토큰이 순서 무관하게 존재
    parts = [p for p in norm_kw.split(" ") if p]
    if len(parts) <= 1:
        return False
    return all(part in norm_text for part in parts)


def count_keyword_matches(text: str, keywords: list[str]) -> int:
    """텍스트에서 매칭되는 키워드 수를 반환."""
    return sum(1 for kw in keywords if keyword_matches_text(text, kw))


def required_keyword_matches(keywords: list[str]) -> int:
    """
    동적 임계값 계산.
    기본: MIN_KEYWORD_MATCHES (2)
    키워드 6개 이상이면 40% 비례 (6개→3개, 10개→4개)
    """
    n = len(keywords)
    if n == 0:
        return 0
    proportional = max(MIN_KEYWORD_MATCHES, int(n * 0.4 + 0.5))  # ceil(n * 0.4)
    return min(n, proportional)


def text_matches_ground_truth(text: str, finding: dict) -> bool:
    """에이전트 텍스트가 ground truth finding에 매칭되는지 확인."""
    keywords = finding.get("keywords", [])
    return count_keyword_matches(text, keywords) >= required_keyword_matches(keywords)


# ============================================================
# 심각도 인접성
# ============================================================

def severity_distance(a: str, b: str) -> int:
    try:
        return abs(SEVERITY_ORDER.index(a.upper()) - SEVERITY_ORDER.index(b.upper()))
    except ValueError:
        return 99


def severity_matches(agent_severity: str, gt_severity: str) -> bool:
    dist = severity_distance(agent_severity, gt_severity)
    return dist <= 1 if ALLOW_ADJACENT_SEVERITY else dist == 0


# ============================================================
# 에이전트 출력 파싱
# ============================================================

def parse_agent_output(text: str) -> dict:
    """
    에이전트 마크다운 출력에서 findings를 추출.
    심각도 섹션 헤더(## CRITICAL, ## MAJOR, ## MINOR, **CRITICAL**, 등) 기반으로 파싱.
    """
    lines = text.split("\n")
    findings = []
    current_severity = "MINOR"
    current_lines: list[str] = []

    severity_pattern = re.compile(
        r"(CRITICAL|MAJOR|MINOR|심각|중요|경고|주의)", re.IGNORECASE
    )
    bullet_pattern = re.compile(r"^[\-\*\•]\s+(.+)$")
    numbered_pattern = re.compile(r"^\d+[\.\)]\s+(.+)$")

    def flush_finding(sev: str, text_lines: list[str]) -> None:
        content = " ".join(t.strip() for t in text_lines if t.strip())
        if not content:
            return
        has_evidence = bool(
            re.search(r"(line\s*\d+|:\d+|\.ts|\.tsx|\.js|\.py|파일|코드)", content, re.IGNORECASE)
        )
        findings.append({
            "text": content,
            "severity": sev.upper() if sev.upper() in SEVERITY_ORDER else "MINOR",
            "has_evidence": has_evidence,
        })

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # 심각도 섹션 헤더 감지
        sev_match = re.search(
            r"\b(CRITICAL|MAJOR|MINOR)\b", stripped, re.IGNORECASE
        )
        is_header = bool(re.match(r"^#{1,4}\s+", stripped)) or bool(
            re.match(r"^\*{1,2}(CRITICAL|MAJOR|MINOR)\*{1,2}", stripped, re.IGNORECASE)
        )

        if is_header and sev_match:
            if current_lines:
                flush_finding(current_severity, current_lines)
                current_lines = []
            current_severity = sev_match.group(1).upper()
            continue

        # 불릿 또는 번호 항목 → 새 finding으로 취급
        bullet_m = bullet_pattern.match(stripped) or numbered_pattern.match(stripped)
        if bullet_m:
            if current_lines:
                flush_finding(current_severity, current_lines)
                current_lines = []
            current_lines = [bullet_m.group(1)]
            # 인라인 심각도 확인
            inline_sev = re.search(r"\b(CRITICAL|MAJOR|MINOR)\b", current_lines[0], re.IGNORECASE)
            if inline_sev:
                current_severity = inline_sev.group(1).upper()
        else:
            # 일반 텍스트 → 현재 finding에 추가
            if sev_match and not is_header:
                current_severity = sev_match.group(1).upper()
            current_lines.append(stripped)

    if current_lines:
        flush_finding(current_severity, current_lines)

    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    major = [f for f in findings if f["severity"] == "MAJOR"]
    minor = [f for f in findings if f["severity"] == "MINOR"]

    return {
        "critical_findings": critical,
        "major_findings": major,
        "minor_findings": minor,
        "all_findings": findings,
        "raw_output": text,
    }


def flatten_findings(parsed: dict) -> list[dict]:
    """파싱된 출력에서 모든 finding을 단일 리스트로 합산."""
    return parsed.get("all_findings", [])


# ============================================================
# 매칭
# ============================================================

def match_findings(parsed: dict, ground_truth: dict) -> dict:
    """
    에이전트 findings를 ground truth findings에 greedy first-match로 매칭.
    각 GT finding은 최대 한 번만 매칭.
    """
    agent_findings = flatten_findings(parsed)
    gt_findings = ground_truth.get("findings", [])

    matched_ids: set[str] = set()
    matched_agent_indices: set[int] = set()

    for gt in gt_findings:
        for i, af in enumerate(agent_findings):
            if i in matched_agent_indices:
                continue
            if text_matches_ground_truth(af["text"], gt):
                matched_ids.add(gt["id"])
                matched_agent_indices.add(i)
                break  # greedy first-match

    missed_ids = [gt["id"] for gt in gt_findings if gt["id"] not in matched_ids]
    spurious_texts = [
        agent_findings[i]["text"]
        for i in range(len(agent_findings))
        if i not in matched_agent_indices
    ]

    return {
        "matched_ids": list(matched_ids),
        "missed_ids": missed_ids,
        "spurious_texts": spurious_texts,
        "total_agent_findings": len(agent_findings),
    }


# ============================================================
# 증거 비율
# ============================================================

def compute_evidence_rate(parsed: dict) -> float:
    high_severity = parsed.get("critical_findings", []) + parsed.get("major_findings", [])
    if not high_severity:
        return 0.0
    with_evidence = sum(1 for f in high_severity if f.get("has_evidence", False))
    return with_evidence / len(high_severity)


# ============================================================
# Fixture 채점
# ============================================================

def score_fixture(parsed: dict, ground_truth: dict) -> dict:
    """
    단일 fixture에 대한 모든 메트릭과 composite score를 계산.
    """
    match = match_findings(parsed, ground_truth)
    matched_ids = match["matched_ids"]
    missed_ids = match["missed_ids"]
    spurious_texts = match["spurious_texts"]
    total_agent = match["total_agent_findings"]

    gt_findings = ground_truth.get("findings", [])
    total_gt = len(gt_findings)

    # 핵심 탐지 메트릭
    true_positive_rate = len(matched_ids) / total_gt if total_gt > 0 else 0.0
    false_negative_rate = len(missed_ids) / total_gt if total_gt > 0 else 0.0
    spurious_rate = len(spurious_texts) / total_agent if total_agent > 0 else 0.0

    # 차원별 커버리지 (카테고리 기반)
    # ground truth의 카테고리별 매칭 비율
    all_gt_ids = {gt["id"] for gt in gt_findings}
    coverage_cats: dict[str, list[str]] = {}
    for gt in gt_findings:
        cat = gt.get("category", "finding")
        coverage_cats.setdefault(cat, []).append(gt["id"])

    category_scores = []
    for cat_ids in coverage_cats.values():
        matched_in_cat = sum(1 for gid in cat_ids if gid in matched_ids)
        category_scores.append(matched_in_cat / len(cat_ids))
    coverage_bonus = sum(category_scores) / len(category_scores) if category_scores else 0.0

    # 증거 포함 비율
    evidence_rate = compute_evidence_rate(parsed)

    # Composite score
    w = WEIGHTS
    composite = (
        w["true_positive_rate"] * true_positive_rate
        + w["false_negative_penalty"] * (1.0 - false_negative_rate)
        + w["spurious_penalty"] * (1.0 - spurious_rate)
        + w["coverage_bonus"] * coverage_bonus
        + w["evidence_rate"] * evidence_rate
    )

    # 심각도별 누락 분류
    missed_by_severity: dict[str, list[str]] = {"CRITICAL": [], "MAJOR": [], "MINOR": []}
    for gt in gt_findings:
        if gt["id"] in missed_ids:
            sev = gt.get("severity", "MINOR").upper()
            missed_by_severity.setdefault(sev, []).append(gt["id"])

    return {
        "fixture_id": ground_truth.get("fixtureId", "unknown"),
        "domain": ground_truth.get("domain", "unknown"),
        "true_positive_rate": round(true_positive_rate, 4),
        "false_negative_rate": round(false_negative_rate, 4),
        "spurious_rate": round(spurious_rate, 4),
        "coverage_bonus": round(coverage_bonus, 4),
        "evidence_rate": round(evidence_rate, 4),
        "composite_score": round(composite, 4),
        "matched_findings": matched_ids,
        "missed_findings": missed_ids,
        "missed_by_severity": missed_by_severity,
        "spurious_findings": spurious_texts[:5],  # 처음 5개만 저장
        "total_gt_findings": total_gt,
        "total_agent_findings": total_agent,
    }


# ============================================================
# 전체 채점
# ============================================================

def score_all(
    ground_truth_dir: Path,
    results_dir: Path | None,
    agent_output_text: str | None,
    fixture_filter: str | None,
) -> dict:
    """
    ground-truth/ 디렉토리의 모든 JSON에 대해 채점 실행.
    results_dir가 있으면 각 fixture ID로 에이전트 출력 파일을 찾음.
    agent_output_text가 있으면 단일 fixture에만 사용.
    """
    gt_files = sorted(ground_truth_dir.glob("*.json"))
    if not gt_files:
        print(f"오류: {ground_truth_dir}에 ground truth JSON 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)

    results = []
    skipped = []

    for gt_path in gt_files:
        fixture_id = gt_path.stem

        if fixture_filter and fixture_id != fixture_filter:
            continue

        # Ground truth 로드
        with open(gt_path, encoding="utf-8") as f:
            ground_truth = json.load(f)

        # 에이전트 출력 로드
        raw_output: str | None = None

        if agent_output_text and (not fixture_filter or fixture_id == fixture_filter):
            raw_output = agent_output_text
        elif results_dir:
            # results_dir에서 fixture_id.txt 또는 fixture_id.md 파일 찾기
            for ext in [".txt", ".md", ".json"]:
                candidate = results_dir / f"{fixture_id}{ext}"
                if candidate.exists():
                    with open(candidate, encoding="utf-8") as f:
                        raw_output = f.read()
                    break

        if raw_output is None:
            skipped.append(fixture_id)
            continue

        # 파싱 및 채점
        parsed = parse_agent_output(raw_output)
        scores = score_fixture(parsed, ground_truth)
        results.append(scores)

    # 집계
    if results:
        aggregate = {
            "true_positive_rate": round(sum(r["true_positive_rate"] for r in results) / len(results), 4),
            "false_negative_rate": round(sum(r["false_negative_rate"] for r in results) / len(results), 4),
            "spurious_rate": round(sum(r["spurious_rate"] for r in results) / len(results), 4),
            "coverage_bonus": round(sum(r["coverage_bonus"] for r in results) / len(results), 4),
            "evidence_rate": round(sum(r["evidence_rate"] for r in results) / len(results), 4),
            "composite_score": round(sum(r["composite_score"] for r in results) / len(results), 4),
        }
    else:
        aggregate = {k: 0.0 for k in ["true_positive_rate", "false_negative_rate", "spurious_rate", "coverage_bonus", "evidence_rate", "composite_score"]}

    # 차원별 집계
    by_dimension: dict[str, list] = {}
    for r in results:
        dim = r["domain"]
        by_dimension.setdefault(dim, []).append(r["composite_score"])
    dimension_scores = {
        dim: round(sum(scores) / len(scores), 4)
        for dim, scores in by_dimension.items()
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fixture_results": results,
        "aggregate": aggregate,
        "dimension_scores": dimension_scores,
        "skipped_fixtures": skipped,
        "total_fixtures": len(results),
    }


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Riff 벤치마크 채점기 — 키워드 매칭 기반 자동 채점",
    )
    parser.add_argument(
        "--ground-truth",
        required=True,
        help="ground-truth/ 디렉토리 경로",
    )
    parser.add_argument(
        "--results-dir",
        default=None,
        help="에이전트 출력 파일 디렉토리 (fixture_id.txt 파일 포함)",
    )
    parser.add_argument(
        "--agent-output",
        default=None,
        help="단일 에이전트 출력 파일 경로 (--fixture와 함께 사용)",
    )
    parser.add_argument(
        "--fixture",
        default=None,
        help="특정 fixture ID만 채점",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="결과 JSON 출력 경로 (미지정 시 stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="JSON 출력을 들여쓰기로 포맷 (기본값: true)",
    )

    args = parser.parse_args()

    gt_dir = Path(args.ground_truth)
    if not gt_dir.exists():
        print(f"오류: ground-truth 디렉토리를 찾을 수 없습니다: {gt_dir}", file=sys.stderr)
        sys.exit(1)

    results_dir: Path | None = None
    if args.results_dir:
        results_dir = Path(args.results_dir)
        if not results_dir.exists():
            print(f"오류: results 디렉토리를 찾을 수 없습니다: {results_dir}", file=sys.stderr)
            sys.exit(1)

    agent_output_text: str | None = None
    if args.agent_output:
        agent_path = Path(args.agent_output)
        if not agent_path.exists():
            print(f"오류: 에이전트 출력 파일을 찾을 수 없습니다: {agent_path}", file=sys.stderr)
            sys.exit(1)
        with open(agent_path, encoding="utf-8") as f:
            agent_output_text = f.read()

    if args.agent_output and not args.fixture:
        print("오류: --agent-output 사용 시 --fixture를 지정해야 합니다.", file=sys.stderr)
        sys.exit(1)

    report = score_all(
        ground_truth_dir=gt_dir,
        results_dir=results_dir,
        agent_output_text=agent_output_text,
        fixture_filter=args.fixture,
    )

    indent = 2 if args.pretty else None
    output_json = json.dumps(report, ensure_ascii=False, indent=indent)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"결과 저장: {out_path}", file=sys.stderr)

        # 요약 출력
        agg = report["aggregate"]
        print(f"\n=== 채점 결과 ===", file=sys.stderr)
        print(f"  fixture 수:      {report['total_fixtures']}", file=sys.stderr)
        print(f"  composite score: {agg['composite_score'] * 100:.1f}%", file=sys.stderr)
        print(f"  TP rate:         {agg['true_positive_rate'] * 100:.1f}%", file=sys.stderr)
        print(f"  FN rate:         {agg['false_negative_rate'] * 100:.1f}%", file=sys.stderr)
        if report["skipped_fixtures"]:
            print(f"  스킵됨: {', '.join(report['skipped_fixtures'])}", file=sys.stderr)
        if report["dimension_scores"]:
            print(f"\n  차원별 점수:", file=sys.stderr)
            for dim, score in report["dimension_scores"].items():
                print(f"    {dim}: {score * 100:.1f}%", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
