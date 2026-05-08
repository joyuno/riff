#!/usr/bin/env python3
"""
Riff 벤치마크 보고서 생성기
scorer.py의 JSON 결과를 마크다운 보고서로 변환합니다.

사용법:
  python reporter.py --input results/output.json --output results/report.md
  python reporter.py --input results/output.json --baseline baselines/baseline_2025-01-01.json
  python reporter.py --compare results/with-riff.json results/without-riff.json --output results/comparison.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================
# 포맷 헬퍼
# ============================================================

def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def sign(value: float) -> str:
    s = pct(abs(value))
    return f"+{s}" if value >= 0 else f"-{s}"


def grade(composite: float) -> str:
    """종합 점수를 S~F 등급으로 변환."""
    if composite >= 0.90:
        return "S"
    elif composite >= 0.80:
        return "A"
    elif composite >= 0.70:
        return "B"
    elif composite >= 0.60:
        return "C"
    elif composite >= 0.50:
        return "D"
    else:
        return "F"


METRIC_LABELS = {
    "true_positive_rate":    "True Positive Rate",
    "false_negative_rate":   "False Negative Rate",
    "spurious_rate":         "Spurious Rate",
    "coverage_bonus":        "Coverage Bonus",
    "evidence_rate":         "Evidence Rate",
    "composite_score":       "Composite Score",
}

DIMENSION_LABELS = {
    "plan":     "인터뷰 품질 (interview)",
    "code":     "경계면 QA (boundary)",
    "analysis": "Live/면역 QA",
}

REGRESSION_THRESHOLD = 0.01  # 1% 이상 하락 시 회귀 경고


# ============================================================
# 단일 보고서 생성
# ============================================================

def generate_single_report(report: dict, baseline: dict | None = None) -> str:
    lines: list[str] = []
    agg = report.get("aggregate", {})
    composite = agg.get("composite_score", 0.0)
    timestamp = report.get("timestamp", "unknown")
    total = report.get("total_fixtures", 0)

    # 헤더
    lines.append("# Riff 벤치마크 보고서")
    lines.append("")
    lines.append(f"**날짜**: {timestamp}")
    lines.append(f"**Fixture 수**: {total}")
    lines.append(f"**종합 등급**: {grade(composite)} ({pct(composite)})")
    lines.append("")

    # 회귀 감지
    if baseline:
        base_composite = baseline.get("aggregate", {}).get("composite_score", 0.0)
        delta = composite - base_composite
        if delta < -REGRESSION_THRESHOLD:
            lines.append(f"> ⚠️  **회귀 감지**: 베이스라인 대비 {sign(delta)} 하락")
            lines.append("")
        elif delta > REGRESSION_THRESHOLD:
            lines.append(f"> ✅  **향상**: 베이스라인 대비 {sign(delta)} 상승")
            lines.append("")

    # 종합 메트릭 테이블
    lines.append("## 종합 메트릭")
    lines.append("")

    if baseline:
        lines.append("| 메트릭 | 이번 실행 | 베이스라인 | Delta |")
        lines.append("|--------|-----------|-----------|-------|")
        base_agg = baseline.get("aggregate", {})
        for key, label in METRIC_LABELS.items():
            val = agg.get(key, 0.0)
            base_val = base_agg.get(key, 0.0)
            delta = val - base_val
            regression = " ⚠️" if key == "composite_score" and delta < -REGRESSION_THRESHOLD else ""
            lines.append(f"| {label} | {pct(val)} | {pct(base_val)} | {sign(delta)}{regression} |")
    else:
        lines.append("| 메트릭 | 점수 |")
        lines.append("|--------|------|")
        for key, label in METRIC_LABELS.items():
            val = agg.get(key, 0.0)
            lines.append(f"| {label} | {pct(val)} |")

    lines.append("")

    # 차원별 점수
    dim_scores = report.get("dimension_scores", {})
    if dim_scores:
        lines.append("## 차원별 점수")
        lines.append("")
        lines.append("| 차원 | 점수 | 등급 |")
        lines.append("|------|------|------|")
        for dim, score in sorted(dim_scores.items()):
            label = DIMENSION_LABELS.get(dim, dim)
            lines.append(f"| {label} | {pct(score)} | {grade(score)} |")
        lines.append("")

    # Fixture별 상세 결과
    fixture_results = report.get("fixture_results", [])
    if fixture_results:
        lines.append("## Fixture별 상세 결과")
        lines.append("")
        lines.append("| Fixture | Composite | TP | FN | Matched | Missed |")
        lines.append("|---------|-----------|----|----|---------|--------|")

        for r in fixture_results:
            fid = r.get("fixture_id", "unknown")
            comp = r.get("composite_score", 0.0)
            tp = r.get("true_positive_rate", 0.0)
            fn = r.get("false_negative_rate", 0.0)
            matched = len(r.get("matched_findings", []))
            missed = len(r.get("missed_findings", []))
            total_gt = r.get("total_gt_findings", matched + missed)
            lines.append(
                f"| {fid} | {pct(comp)} | {pct(tp)} | {pct(fn)} | {matched}/{total_gt} | {missed} |"
            )

        lines.append("")

        # 누락된 CRITICAL findings 경고
        critical_misses = []
        for r in fixture_results:
            missed_by_sev = r.get("missed_by_severity", {})
            crit_missed = missed_by_sev.get("CRITICAL", [])
            if crit_missed:
                critical_misses.append((r["fixture_id"], crit_missed))

        if critical_misses:
            lines.append("### CRITICAL Finding 누락 경고")
            lines.append("")
            for fid, ids in critical_misses:
                lines.append(f"- **{fid}**: {', '.join(ids)} 누락")
            lines.append("")

    # 스킵된 fixtures
    skipped = report.get("skipped_fixtures", [])
    if skipped:
        lines.append("## 스킵된 Fixture")
        lines.append("")
        lines.append("_에이전트 출력 파일을 찾지 못해 채점에서 제외됨_")
        lines.append("")
        for fid in skipped:
            lines.append(f"- {fid}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# 비교 보고서 생성 (With-Riff vs Without-Riff)
# ============================================================

def generate_comparison_report(with_riff: dict, without_riff: dict) -> str:
    lines: list[str] = []

    wp_agg = with_riff.get("aggregate", {})
    wop_agg = without_riff.get("aggregate", {})

    wp_composite = wp_agg.get("composite_score", 0.0)
    wop_composite = wop_agg.get("composite_score", 0.0)
    overall_delta = wp_composite - wop_composite

    lines.append("# Riff 벤치마크 비교 보고서")
    lines.append("")
    lines.append("## With-Riff vs Without-Riff")
    lines.append("")
    lines.append(f"| | With Riff | Without Riff | Delta |")
    lines.append(f"|---|-----------|---------------|-------|")
    lines.append(
        f"| **Composite Score** | {pct(wp_composite)} ({grade(wp_composite)}) | "
        f"{pct(wop_composite)} ({grade(wop_composite)}) | **{sign(overall_delta)}** |"
    )
    lines.append("")

    # 메트릭별 비교
    lines.append("## 메트릭별 비교")
    lines.append("")
    lines.append("| 메트릭 | With Riff | Without Riff | Delta |")
    lines.append("|--------|-----------|---------------|-------|")

    for key, label in METRIC_LABELS.items():
        wp_val = wp_agg.get(key, 0.0)
        wop_val = wop_agg.get(key, 0.0)
        delta = wp_val - wop_val
        lines.append(f"| {label} | {pct(wp_val)} | {pct(wop_val)} | {sign(delta)} |")

    lines.append("")

    # Fixture별 Head-to-Head
    wp_fixtures = {r["fixture_id"]: r for r in with_riff.get("fixture_results", [])}
    wop_fixtures = {r["fixture_id"]: r for r in without_riff.get("fixture_results", [])}
    all_fixture_ids = sorted(set(wp_fixtures) | set(wop_fixtures))

    if all_fixture_ids:
        lines.append("## Fixture별 Head-to-Head")
        lines.append("")
        lines.append("| Fixture | With Riff | Without Riff | Delta | Winner |")
        lines.append("|---------|-----------|---------------|-------|--------|")

        wp_wins = 0
        wop_wins = 0
        ties = 0

        for fid in all_fixture_ids:
            wp_r = wp_fixtures.get(fid)
            wop_r = wop_fixtures.get(fid)
            wp_score = wp_r["composite_score"] if wp_r else 0.0
            wop_score = wop_r["composite_score"] if wop_r else 0.0
            delta = wp_score - wop_score

            if abs(delta) < 0.001:
                winner = "동점"
                ties += 1
            elif delta > 0:
                winner = "With Riff ✓"
                wp_wins += 1
            else:
                winner = "Without Riff"
                wop_wins += 1

            lines.append(
                f"| {fid} | {pct(wp_score)} | {pct(wop_score)} | {sign(delta)} | {winner} |"
            )

        lines.append("")
        lines.append(
            f"**종합**: With Riff {wp_wins}승 / Without Riff {wop_wins}승 / 동점 {ties}"
        )
        lines.append("")

    # 차원별 비교
    wp_dims = with_riff.get("dimension_scores", {})
    wop_dims = without_riff.get("dimension_scores", {})
    all_dims = sorted(set(wp_dims) | set(wop_dims))

    if all_dims:
        lines.append("## 차원별 Riff 효과")
        lines.append("")
        lines.append("| 차원 | With Riff | Without Riff | Riff 효과 |")
        lines.append("|------|-----------|---------------|-----------|")

        for dim in all_dims:
            wp_score = wp_dims.get(dim, 0.0)
            wop_score = wop_dims.get(dim, 0.0)
            delta = wp_score - wop_score
            label = DIMENSION_LABELS.get(dim, dim)
            lines.append(f"| {label} | {pct(wp_score)} | {pct(wop_score)} | {sign(delta)} |")

        lines.append("")

    # Key Insight
    lines.append("## 핵심 인사이트")
    lines.append("")
    if overall_delta > 0.10:
        lines.append(
            f"Riff 적용 시 종합 점수가 **{sign(overall_delta)}** 향상됩니다. "
            f"특히 인터뷰 품질과 경계면 QA 차원에서 효과가 두드러집니다."
        )
    elif overall_delta > 0:
        lines.append(
            f"Riff 적용 시 종합 점수가 {sign(overall_delta)} 향상됩니다."
        )
    elif overall_delta < -REGRESSION_THRESHOLD:
        lines.append(
            f"⚠️  Without Riff가 {sign(-overall_delta)} 높은 점수를 기록했습니다. "
            f"Riff 시스템 점검이 필요합니다."
        )
    else:
        lines.append("두 실행 결과가 유사합니다. 추가 fixture가 필요할 수 있습니다.")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Riff 벤치마크 보고서 생성기",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="scorer.py 출력 JSON 파일 경로",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="베이스라인 JSON 파일 경로 (비교용)",
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("WITH_RIFF_JSON", "WITHOUT_RIFF_JSON"),
        help="With-Riff vs Without-Riff 비교 모드",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="마크다운 보고서 출력 경로 (미지정 시 stdout)",
    )

    args = parser.parse_args()

    if args.compare:
        # 비교 모드
        with_path, without_path = args.compare
        with open(with_path, encoding="utf-8") as f:
            with_riff = json.load(f)
        with open(without_path, encoding="utf-8") as f:
            without_riff = json.load(f)
        report_md = generate_comparison_report(with_riff, without_riff)

    elif args.input:
        # 단일 보고서 모드
        with open(args.input, encoding="utf-8") as f:
            report = json.load(f)

        baseline: dict | None = None
        if args.baseline:
            with open(args.baseline, encoding="utf-8") as f:
                baseline = json.load(f)

        report_md = generate_single_report(report, baseline)

    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"보고서 저장: {out_path}", file=sys.stderr)
    else:
        print(report_md)


if __name__ == "__main__":
    main()
