#!/usr/bin/env python3
"""Score repeated adaptive-depth decisions against v1 ground truth."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Sequence


PROFILES = ("단순", "보통", "복잡")


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def selected_profile(text: str) -> str | None:
    match = re.search(r"(?:depth\s*)?(?:프로파일|판정)\s*[:：]?\s*(단순|보통|복잡)", text, re.I)
    return match.group(1) if match else None


def has_frame_or_assumption(text: str) -> bool:
    return bool(re.search(r"가정\s*선언|FRAME\s*(?:질문|확인)|프레임\s*질문", text, re.I))


def has_status_assumption(text: str) -> bool:
    status = re.search(r"##\s*STATUS\b(?P<body>.*?)(?=\n##\s|\Z)", text, re.I | re.S)
    return bool(status and re.search(r"활성\s*가정", status.group("body")))


FRAME_SKIP = re.compile(r"FRAME(?:을|를|은|는)?\s*(?:완전히?\s*)?(?:스킵|생략)", re.I)

# 한국어 부정은 서술어 뒤에 붙는다("스킵 금지", "스킵하지 않고"). 매칭 직후 짧은 창에
# 부정어가 있으면 "스킵하면 안 된다"는 올바른 판정이므로 위반으로 세지 않는다.
NEGATION = re.compile(r"금지|불가|안\s*된|않|말아야|말고|못한|아니")
NEGATION_WINDOW = 10


def find_violations(text: str) -> list[str]:
    violations: list[str] = []
    match = FRAME_SKIP.search(text)
    while match:
        if not NEGATION.search(text[match.end() : match.end() + NEGATION_WINDOW]):
            violations.append("FRAME 완전 스킵")
            break
        match = FRAME_SKIP.search(text, match.end())
    if re.search(r"BUILD\s*진입", text, re.I) and not re.search(r"성공\s*기준", text):
        violations.append("성공 기준 없이 BUILD 진입")
    return violations


def score_run(output: str, ground_truth: dict) -> dict:
    text = normalize(output)
    profile = selected_profile(text)
    missing: list[str] = []

    if profile is None:
        missing.append("depth 프로파일")
    elif profile != ground_truth["expected_profile"]:
        alternative = ground_truth.get("allow_alternative", "")
        if not (profile == "보통" and alternative.startswith("보통+") and has_frame_or_assumption(text)):
            missing.append("허용된 depth 판정")

    for requirement in ground_truth.get("must_have", []):
        if requirement == "가정 선언 또는 FRAME 질문" and not has_frame_or_assumption(text):
            missing.append(requirement)
        elif requirement == "STATUS 활성 가정 노출" and not has_status_assumption(text):
            missing.append(requirement)

    violations = find_violations(text)

    return {
        "selected_profile": profile,
        "missing_requirements": missing,
        "violations": violations,
        "valid": not missing and not violations,
    }


def score_fixture(outputs: Sequence[str], ground_truth: dict) -> dict:
    if not outputs:
        raise ValueError("at least one output is required")
    runs = [score_run(output, ground_truth) for output in outputs]
    profiles = [run["selected_profile"] for run in runs]
    decision_consistent = len(set(profiles)) == 1
    pass_rate = round(sum(run["valid"] for run in runs) / len(runs), 4)
    return {
        "scenario": ground_truth.get("scenario", "unknown"),
        "runs": runs,
        "repetitions": len(runs),
        "pass_rate": pass_rate,
        "decision_consistent": decision_consistent,
        "passed": pass_rate == 1.0 and decision_consistent,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument("--output", action="append", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ground_truth = json.loads(args.ground_truth.read_text(encoding="utf-8"))
    outputs = [path.read_text(encoding="utf-8") for path in args.output]
    report = score_fixture(outputs, ground_truth)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
