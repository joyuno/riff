#!/usr/bin/env python3
"""Deterministic wall-clock overhead calculator for Riff benchmarks."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Sequence


class ValidationError(ValueError):
    """Raised when timing samples cannot produce a meaningful comparison."""


def calculate_report(
    baseline_ms: Sequence[int],
    riff_ms: Sequence[int],
    budget_percent: float = 15.0,
) -> dict:
    baseline = list(baseline_ms)
    riff = list(riff_ms)

    if not baseline or not riff:
        raise ValidationError("timing samples must not be empty")
    if len(baseline) != len(riff):
        raise ValidationError("baseline and riff sample counts must match")
    if any(value <= 0 for value in baseline + riff):
        raise ValidationError("all timing samples must be positive milliseconds")
    if budget_percent < 0:
        raise ValidationError("budget percent must not be negative")

    baseline_median = statistics.median(baseline)
    riff_median = statistics.median(riff)
    overhead = round(((riff_median - baseline_median) / baseline_median) * 100, 4)

    return {
        "baseline_ms": baseline,
        "riff_ms": riff,
        "repetitions": len(baseline),
        "baseline_median_ms": baseline_median,
        "riff_median_ms": riff_median,
        "overhead_percent": overhead,
        "budget_percent": budget_percent,
        "passed": overhead <= budget_percent,
    }


def parse_samples(raw: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise ValidationError("timings must be comma-separated integers") from exc
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ms", required=True)
    parser.add_argument("--riff-ms", required=True)
    parser.add_argument("--budget-percent", type=float, default=15.0)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = calculate_report(
            parse_samples(args.baseline_ms),
            parse_samples(args.riff_ms),
            args.budget_percent,
        )
    except ValidationError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
