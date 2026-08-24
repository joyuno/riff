#!/usr/bin/env python3
"""기록된 depth 판정을 정답률·재현성 두 축으로 채점한다.

판정 수집은 사람이 하고 이 스크립트는 채점만 한다(bench.py와 같은 구조).
입력은 blind 반복 판정을 모은 JSON 배열:

    [{"fixture": "depth-ambiguous-notes", "profile": "복잡",
      "signals": 3, "declared_assumption": true, "raw": "..."}, ...]

`kind`는 raw가 무엇인지 알린다: "verdict"(기본, 판정 근거 문단) 또는 "full-output"(riff 사이클
전체 출력). verdict 입력에는 전체 출력 구조를 요구하는 must_have를 적용하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

BENCHMARKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BENCHMARKS_DIR))

from scoring.depth_reproducibility import (  # noqa: E402
    find_violations,
    has_frame_or_assumption,
    has_status_assumption,
    normalize,
)

GROUND_TRUTH_DIR = BENCHMARKS_DIR / "ground-truth"

# 판정 단위 입력(kind="verdict")의 raw는 depth 판정 근거 문단이지 riff 사이클 전체 출력이 아니다.
# ground truth의 must_have 중 "STATUS 활성 가정 노출"만 riff가 사이클 끝에 렌더하는
# `## STATUS` 섹션 구조를 요구하므로 판정 문단으로는 구조상 충족 불가 — 전체 출력에서만 검사한다.
# 나머지("가정 선언 또는 FRAME 질문")는 판정 근거 문단 안에서 그대로 확인 가능하다.
FULL_OUTPUT_ONLY_REQUIREMENTS = frozenset({"STATUS 활성 가정 노출"})
VERDICT_KINDS = ("verdict", "full-output")


def load_ground_truth(fixture: str) -> dict:
    path = GROUND_TRUTH_DIR / f"{fixture}.json"
    if not path.is_file():
        raise SystemExit(f"ground truth 없음: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_verdicts(path: Path) -> list[dict]:
    verdicts = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(verdicts, list) or not verdicts:
        raise SystemExit("verdicts는 비어 있지 않은 배열이어야 합니다")
    for index, verdict in enumerate(verdicts):
        if not isinstance(verdict, dict):
            raise SystemExit(f"verdicts[{index}]는 객체가 아닙니다")
        for field in ("fixture", "profile"):
            if not verdict.get(field):
                raise SystemExit(f"verdicts[{index}]에 '{field}' 필드가 없습니다")
        if verdict.get("kind", "verdict") not in VERDICT_KINDS:
            raise SystemExit(f"verdicts[{index}]의 kind는 {VERDICT_KINDS} 중 하나여야 합니다")
    return verdicts


def declared_assumption(verdict: dict) -> bool:
    """기록된 플래그 우선, 없으면 raw에서 가정 선언/FRAME 질문을 찾는다."""
    declared = verdict.get("declared_assumption")
    if declared is None:
        return has_frame_or_assumption(normalize(verdict.get("raw", "")))
    return bool(declared)


def grade_profile(verdict: dict, ground_truth: dict) -> str:
    """'exact' | 'alternative' | 'wrong' | 'unscored'.

    depth 정답이 없는 ground truth(예: 인터뷰 픽스처)는 'unscored' — 재현성만 집계한다.
    """
    profile = verdict["profile"]
    if "expected_profile" not in ground_truth:
        return "unscored"
    if profile == ground_truth["expected_profile"]:
        return "exact"
    alternative = ground_truth.get("allow_alternative", "")
    if alternative:
        alt_profile, _, condition = alternative.partition("+")
        if profile == alt_profile and (not condition or declared_assumption(verdict)):
            return "alternative"
    return "wrong"


def check_keywords(verdict: dict, ground_truth: dict) -> tuple[list[str], list[str], list[str]]:
    """must_have 누락·판정 제외와 must_not 위반을 raw 필드에서 찾는다."""
    text = normalize(verdict.get("raw", ""))
    full_output = verdict.get("kind", "verdict") == "full-output"
    missing: list[str] = []
    excluded: list[str] = []
    for requirement in ground_truth.get("must_have", []):
        if not full_output and requirement in FULL_OUTPUT_ONLY_REQUIREMENTS:
            excluded.append(requirement)
            continue
        if requirement == "가정 선언 또는 FRAME 질문":
            satisfied = has_frame_or_assumption(text)
        elif requirement == "STATUS 활성 가정 노출":
            satisfied = has_status_assumption(text)
        else:
            satisfied = requirement in text
        if not satisfied:
            missing.append(requirement)
    return missing, find_violations(text), excluded


def score_fixture(fixture: str, verdicts: Sequence[dict], ground_truth: dict) -> dict:
    runs = []
    for verdict in verdicts:
        missing, violations, excluded = check_keywords(verdict, ground_truth)
        runs.append(
            {
                "profile": verdict["profile"],
                "kind": verdict.get("kind", "verdict"),
                "signals": verdict.get("signals"),
                "declared_assumption": declared_assumption(verdict),
                "grade": grade_profile(verdict, ground_truth),
                "missing_requirements": missing,
                "excluded_requirements": excluded,
                "violations": violations,
            }
        )

    total = len(runs)
    grades = Counter(run["grade"] for run in runs)
    modal_profile, modal_count = Counter(run["profile"] for run in runs).most_common(1)[0]
    signals = [run["signals"] for run in runs if isinstance(run["signals"], (int, float))]
    correct = grades["exact"] + grades["alternative"]
    graded = total - grades["unscored"]
    missing_total = sum(len(run["missing_requirements"]) for run in runs)
    excluded_total = sum(len(run["excluded_requirements"]) for run in runs)
    violation_total = sum(len(run["violations"]) for run in runs)

    return {
        "fixture": fixture,
        "repetitions": total,
        "graded": graded,
        "exact": grades["exact"],
        "alternative": grades["alternative"],
        "wrong": grades["wrong"],
        "accuracy": round(correct / graded, 4) if graded else None,
        "exact_accuracy": round(grades["exact"] / graded, 4) if graded else None,
        "consistency": round(modal_count / total, 4),
        "modal_profile": modal_profile,
        "mean_signals": round(sum(signals) / len(signals), 2) if signals else None,
        "missing_total": missing_total,
        "excluded_total": excluded_total,
        "violation_total": violation_total,
        "runs": runs,
        "passed": (
            correct == graded
            and modal_count == total
            and missing_total == 0
            and violation_total == 0
        ),
    }


def score_all(verdicts: Sequence[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for verdict in verdicts:
        grouped.setdefault(verdict["fixture"], []).append(verdict)

    fixtures = [
        score_fixture(fixture, items, load_ground_truth(fixture))
        for fixture, items in grouped.items()
    ]
    total = sum(item["repetitions"] for item in fixtures)
    graded = sum(item["graded"] for item in fixtures)
    correct = sum(item["exact"] + item["alternative"] for item in fixtures)
    exact = sum(item["exact"] for item in fixtures)
    consistency = sum(item["consistency"] for item in fixtures) / len(fixtures)

    return {
        "fixtures": fixtures,
        "total_verdicts": total,
        "graded_verdicts": graded,
        "accuracy": round(correct / graded, 4) if graded else None,
        "exact_accuracy": round(exact / graded, 4) if graded else None,
        "alternative_count": sum(item["alternative"] for item in fixtures),
        "consistency": round(consistency, 4),
        "violation_total": sum(item["violation_total"] for item in fixtures),
        "missing_total": sum(item["missing_total"] for item in fixtures),
        "excluded_total": sum(item["excluded_total"] for item in fixtures),
        "passed": all(item["passed"] for item in fixtures),
    }


def percent(value: float | None) -> str:
    """depth 정답이 없어 집계 대상이 아니면 '-'."""
    return "-" if value is None else f"{value:.0%}"


def render(report: dict) -> str:
    lines = [
        "| 픽스처 | 판정 | 정답 | 대안 | 오답 | 정답률 | 재현성 | 최빈 | 신호평균 | 위반 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for item in report["fixtures"]:
        signals = "-" if item["mean_signals"] is None else f"{item['mean_signals']}"
        lines.append(
            f"| {item['fixture']} | {item['repetitions']} | {item['exact']} | "
            f"{item['alternative']} | {item['wrong']} | {percent(item['accuracy'])} | "
            f"{item['consistency']:.0%} | {item['modal_profile']} | {signals} | "
            f"{item['violation_total']} |"
        )

    lines.append("")
    lines.append(
        f"종합: 판정 {report['total_verdicts']}건(채점 대상 {report['graded_verdicts']}건) · "
        f"정답률 {percent(report['accuracy'])} "
        f"(정확 {percent(report['exact_accuracy'])} + 대안 {report['alternative_count']}건) · "
        f"재현성 {report['consistency']:.0%} · "
        f"must_have 누락 {report['missing_total']} · must_not 위반 {report['violation_total']} · "
        f"판정 제외 {report['excluded_total']}건"
    )

    for item in report["fixtures"]:
        for index, run in enumerate(item["runs"], start=1):
            for requirement in run["missing_requirements"]:
                lines.append(f"  - {item['fixture']} #{index} 누락: {requirement}")
            for requirement in run["excluded_requirements"]:
                lines.append(
                    f"  - {item['fixture']} #{index} 판정 제외: {requirement} (전체 출력 전용)"
                )
            for violation in run["violations"]:
                lines.append(f"  - {item['fixture']} #{index} 위반: {violation}")

    lines.append("PASS: 정답률·재현성 100%" if report["passed"] else "FAIL: 정답률 또는 재현성 미달")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdicts", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="JSON 리포트로 출력")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = score_all(load_verdicts(args.verdicts))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
