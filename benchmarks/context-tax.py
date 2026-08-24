#!/usr/bin/env python3
"""speed-tax — riff 문서가 먹는 컨텍스트 세금 측정.

wall-clock은 재지 않는다. 프리플라이트 v2·v3에서 n=1·실행자 교란으로 ±4 분산이
나와 설계 효과를 재지 못했다(benchmarks/mvp-bench/preflight/RESULTS-V3.md).
대신 결정적으로 잴 수 있는 것을 잰다 — depth 프로파일별로 riff가 사이클 핫패스에서
읽는 문서의 문자 수와 추정 토큰, 그리고 모델 컨텍스트 창 대비 비율.

검사 대상 가설: progressive disclosure가 실제로 작동하는가
(단순 < 보통 < 복잡 으로 단조 증가하는가).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "riff"
SKILL_MD = SKILL_DIR / "SKILL.md"

# 모든 프로파일이 사이클 핫패스에서 공통으로 읽는 문서.
#   SKILL.md            — 스킬 본문. 호출 시 항상 컨텍스트에 들어간다.
#   canvas-schema.md    — SKILL "캔버스" 절: CANVAS.md 생성·유지에 매 사이클 필요.
#   frame.md            — 단순도 "FRAME 스킵 가드 확인 후 가정 선언"이라 읽어야 한다.
#   build.md            — BUILD 스테이지 세부. depth 무관 실행.
#   learn.md            — LEARN 스테이지 세부. depth 무관 실행.
BASE = [
    "SKILL.md",
    "references/canvas-schema.md",
    "references/frame.md",
    "references/build.md",
    "references/learn.md",
]

# depth 판정표(SKILL.md "depth 판정")와 frame.md "depth별 동작"에서 그대로 옮긴 규칙.
PROFILE_LOADS = {
    # 6+/8 — FRAME 스킵 가드 → 가정 선언, SHAPE 스킵, PROVE-lite(Tier 0+2).
    #   Tier 0 = canvas-lint.md("canvas-lint — Tier 0 기계적 술어 6종"),
    #   Tier 2 = tier2-build.md(자체 명시: "단순 depth의 PROVE-lite(= Tier 0+2)").
    #   SHAPE 스킵이므로 shape-jam.md 없음. diff-review 없음.
    "단순": BASE + [
        "references/prove/canvas-lint.md",
        "references/prove/tier2-build.md",
    ],
    # 4~5/8 — FRAME 2문항, PROVE Tier 0~2 + 인라인 diff-review.
    #   SHAPE는 스킵되지 않으므로 shape-jam.md 추가. Tier 1 = tier1-boundary.md.
    "보통": BASE + [
        "references/shape-jam.md",
        "references/prove/canvas-lint.md",
        "references/prove/tier1-boundary.md",
        "references/prove/tier2-build.md",
        "references/prove/diff-review.md",
    ],
    # <4/8 — 풀 스테이지 + 잼 + Tier 0~3 + 독립 diff-review.
    #   FRAME 복잡 = 5-Layer 인터뷰(layers + enriched-layers) + 도메인 분기(domains/).
    #   도메인은 Router가 하나만 고른다 → frame.md 웹앱 fast-path 기본값인
    #   web-development.md 1개만 계산(--domain 으로 교체 가능).
    #   domain-intelligence(Router) / discovery-research(조사) / termination-engine(게이트 태그)은
    #   frame.md 본문이 Cycle 0 흐름으로 지목한다.
    "복잡": BASE + [
        "references/shape-jam.md",
        "references/frame/layers.md",
        "references/frame/enriched-layers.md",
        "references/frame/domain-intelligence.md",
        "references/frame/discovery-research.md",
        "references/frame/termination-engine.md",
        "references/frame/domains/web-development.md",
        "references/prove/canvas-lint.md",
        "references/prove/tier1-boundary.md",
        "references/prove/tier2-build.md",
        "references/prove/tier3-live.md",
        "references/prove/diff-review.md",
    ],
}

# 핫패스 밖 — 조건부라서 어느 프로파일에도 상시 계산하지 않는다. 커버리지 경고에서 제외.
OFF_HOTPATH = {
    "references/companions.md",       # Bootstrap 1회
    "references/drop.md",             # 이벤트 스테이지
    "references/tune.md",             # 이벤트 스테이지
    "references/convergence.md",      # DROP 판정
    "references/rewind-protocol.md",  # 3회 연속 실패 시
    "references/model-routing.md",    # 스폰 시
    "references/ui-stack-guide.md",   # UI 있을 때 Cycle 0 1회
}

# 한국어·영어 혼용이라 토큰/문자 비율이 넓게 흔들린다. 단일 근사로 숨기지 않고
# 경계 둘을 함께 낸다: 영문·마크다운 위주면 ~3.5자/토큰, 한글 위주면 ~2자/토큰.
CHARS_PER_TOKEN_LOW = 3.5   # 낙관 경계(토큰 적게 나옴)
CHARS_PER_TOKEN_HIGH = 2.0  # 비관 경계(토큰 많이 나옴)


def measure(paths: list[str], root: Path) -> dict:
    files = []
    total = 0
    for rel in paths:
        f = root / rel
        if not f.is_file():
            raise SystemExit(f"문서 없음: {f} — PROFILE_LOADS가 실제 파일과 어긋났다")
        n = len(f.read_text(encoding="utf-8"))
        files.append({"path": rel, "chars": n})
        total += n
    return {
        "files": files,
        "file_count": len(files),
        "chars": total,
        "tokens_low": round(total / CHARS_PER_TOKEN_LOW),
        "tokens_high": round(total / CHARS_PER_TOKEN_HIGH),
    }


def verdict(low_pct: float, high_pct: float, budget: float) -> str:
    if high_pct <= budget:
        return "PASS"
    if low_pct > budget:
        return "OVER"
    return "BORDER"  # 추정 불확실성이 예산선을 걸친다 — 단정하지 않는다


def coverage_gaps(root: Path) -> list[str]:
    """SKILL.md가 지목하는데 어느 프로파일에도 안 잡힌 references 경로."""
    mentioned = set(re.findall(r"references/[\w./-]+\.md", SKILL_MD.read_text(encoding="utf-8")))
    loaded = {p for paths in PROFILE_LOADS.values() for p in paths}
    return sorted(mentioned - loaded - OFF_HOTPATH)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="riff 문서 컨텍스트 세금 측정")
    ap.add_argument("--budget", type=float, default=15.0, help="예산 (컨텍스트 창 대비 %%, 기본 15)")
    ap.add_argument("--window", type=int, default=200_000, help="모델 컨텍스트 창 토큰 (기본 200000)")
    ap.add_argument("--json", action="store_true", help="기계 판독 출력")
    ap.add_argument("--root", type=Path, default=SKILL_DIR, help="skills/riff 경로")
    ap.add_argument("--selftest", action="store_true", help="자체 검사 실행")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    report = {"window": args.window, "budget_percent": args.budget, "profiles": {}}
    for name, paths in PROFILE_LOADS.items():
        m = measure(paths, args.root)
        low_pct = m["tokens_low"] / args.window * 100
        high_pct = m["tokens_high"] / args.window * 100
        m["window_percent_low"] = round(low_pct, 2)
        m["window_percent_high"] = round(high_pct, 2)
        m["verdict"] = verdict(low_pct, high_pct, args.budget)
        report["profiles"][name] = m

    order = [report["profiles"][n]["chars"] for n in ("단순", "보통", "복잡")]
    report["monotonic"] = order == sorted(order) and len(set(order)) == 3
    report["coverage_gaps"] = coverage_gaps(args.root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"riff 문서 컨텍스트 세금 (창 {args.window:,} 토큰, 예산 {args.budget}%)")
    print("측정 대상: 문서 토큰량. wall-clock은 측정하지 않는다.\n")
    print(f"{'프로파일':<8} {'파일':>4} {'문자':>8} {'토큰(저~고)':>16} {'창 대비':>16}  판정")
    print("-" * 70)
    for name in ("단순", "보통", "복잡"):
        m = report["profiles"][name]
        tok = f"{m['tokens_low']:,}~{m['tokens_high']:,}"
        pct = f"{m['window_percent_low']}%~{m['window_percent_high']}%"
        print(f"{name:<8} {m['file_count']:>4} {m['chars']:>8,} {tok:>16} {pct:>16}  {m['verdict']}")
    print()
    print(f"progressive disclosure 단조 증가: {'YES' if report['monotonic'] else 'NO'}")
    if report["coverage_gaps"]:
        print("커버리지 경고 — SKILL.md가 지목하나 어느 프로파일에도 없음:")
        for g in report["coverage_gaps"]:
            print(f"  - {g}")
    return 0


def selftest() -> int:
    assert verdict(1.0, 2.0, 15) == "PASS"
    assert verdict(20.0, 30.0, 15) == "OVER"
    assert verdict(10.0, 20.0, 15) == "BORDER"
    assert set(PROFILE_LOADS["단순"]) < set(PROFILE_LOADS["보통"]) < set(PROFILE_LOADS["복잡"]), \
        "프로파일 로드 집합은 포함 관계여야 한다"
    m = measure(BASE, SKILL_DIR)
    assert m["chars"] > 0 and m["tokens_low"] < m["tokens_high"]
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
