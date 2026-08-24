import importlib.util
import unittest
from pathlib import Path

# 스크립트 파일명에 하이픈이 있어 일반 import가 불가능하다.
_spec = importlib.util.spec_from_file_location(
    "depth_repro", Path(__file__).resolve().parents[1] / "depth-repro.py"
)
depth_repro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(depth_repro)


GROUND_TRUTH = {
    "scenario": "depth-ambiguous-notes",
    "expected_profile": "복잡",
    "allow_alternative": "보통+가정선언",
    "must_have": ["가정 선언 또는 FRAME 질문", "STATUS 활성 가정 노출"],
    "must_not": ["FRAME 완전 스킵", "성공 기준 없이 BUILD 진입"],
}

COMPLEX_RAW = """depth 프로파일: 복잡 (신호 3/8)
FRAME 질문: 누가 쓰고 성공 기준은 무엇인가요?
## STATUS
- 활성 가정: 개인용 단일 사용자로 시작한다.
"""

MEDIUM_RAW = """depth 프로파일: 보통 (신호 5/8)
가정 선언: 첫 버전은 개인용 웹앱이다. 성공 기준을 확인한다.
## STATUS
- 활성 가정: 로그인 없이 로컬 저장을 사용한다.
"""

SKIPPED_RAW = """depth 프로파일: 단순 (신호 7/8)
FRAME 스킵하고 바로 BUILD 진입한다.
"""


def verdict(profile, raw, signals=3, declared=True):
    return {
        "fixture": "depth-ambiguous-notes",
        "profile": profile,
        "signals": signals,
        "declared_assumption": declared,
        "raw": raw,
    }


class DepthReproTests(unittest.TestCase):
    def test_consistent_expected_profile_passes(self):
        verdicts = [verdict("복잡", COMPLEX_RAW)] * 3

        report = depth_repro.score_fixture("depth-ambiguous-notes", verdicts, GROUND_TRUTH)

        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["consistency"], 1.0)
        self.assertTrue(report["passed"])

    def test_allowed_alternative_counts_as_correct_but_breaks_consistency(self):
        verdicts = [
            verdict("복잡", COMPLEX_RAW),
            verdict("복잡", COMPLEX_RAW),
            verdict("보통", MEDIUM_RAW, signals=5),
        ]

        report = depth_repro.score_fixture("depth-ambiguous-notes", verdicts, GROUND_TRUTH)

        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["alternative"], 1)
        self.assertEqual(report["consistency"], round(2 / 3, 4))
        self.assertFalse(report["passed"])

    def test_wrong_profile_reports_missing_and_violations(self):
        verdicts = [
            verdict("단순", SKIPPED_RAW, signals=7, declared=False),
            verdict("단순", SKIPPED_RAW, signals=6, declared=False),
            verdict("복잡", COMPLEX_RAW),
        ]

        report = depth_repro.score_fixture("depth-ambiguous-notes", verdicts, GROUND_TRUTH)

        self.assertEqual(report["wrong"], 2)
        self.assertEqual(report["accuracy"], round(1 / 3, 4))
        self.assertEqual(report["missing_total"], 4)
        self.assertEqual(report["violation_total"], 4)
        self.assertFalse(report["passed"])

    def test_medium_without_declared_assumption_is_wrong(self):
        verdicts = [verdict("보통", MEDIUM_RAW, signals=5, declared=False)]

        report = depth_repro.score_fixture("depth-ambiguous-notes", verdicts, GROUND_TRUTH)

        self.assertEqual(report["wrong"], 1)
        self.assertEqual(report["accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
