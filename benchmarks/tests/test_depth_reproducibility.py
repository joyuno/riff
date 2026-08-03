import unittest

from benchmarks.scoring.depth_reproducibility import score_fixture, score_run


GROUND_TRUTH = {
    "scenario": "depth-ambiguous-notes",
    "expected_profile": "복잡",
    "allow_alternative": "보통+가정선언",
    "must_have": ["가정 선언 또는 FRAME 질문", "STATUS 활성 가정 노출"],
    "must_not": ["FRAME 완전 스킵", "성공 기준 없이 BUILD 진입"],
}

COMPLEX_OUTPUT = """
depth 프로파일: 복잡 (신호 4/8)
FRAME 질문: 누가 이 메모를 사용하며 성공 기준은 무엇인가요?
## STATUS
- 활성 가정: 동기화 범위는 단일 사용자로 시작한다.
"""

MEDIUM_WITH_ASSUMPTION = """
depth 프로파일: 보통 (신호 2/8)
가정 선언: 첫 버전은 개인용 웹앱이다.
FRAME 질문: 성공 기준을 확인한다.
## STATUS
- 활성 가정: 로그인 없이 로컬 저장을 사용한다.
"""


class DepthRunTests(unittest.TestCase):
    def test_accepts_expected_complex_profile(self):
        result = score_run(COMPLEX_OUTPUT, GROUND_TRUTH)

        self.assertEqual(result["selected_profile"], "복잡")
        self.assertTrue(result["valid"])
        self.assertEqual(result["violations"], [])

    def test_accepts_medium_only_with_declared_assumption(self):
        result = score_run(MEDIUM_WITH_ASSUMPTION, GROUND_TRUTH)

        self.assertEqual(result["selected_profile"], "보통")
        self.assertTrue(result["valid"])

    def test_rejects_missing_status_assumption(self):
        output = "depth 프로파일: 보통\n가정 선언: 개인용이다.\nFRAME 질문: 성공 기준은?"

        result = score_run(output, GROUND_TRUTH)

        self.assertFalse(result["valid"])
        self.assertIn("STATUS 활성 가정 노출", result["missing_requirements"])

    def test_rejects_explicit_frame_skip(self):
        output = COMPLEX_OUTPUT + "\nFRAME 완전 스킵 후 구현한다."

        result = score_run(output, GROUND_TRUTH)

        self.assertFalse(result["valid"])
        self.assertIn("FRAME 완전 스킵", result["violations"])

    def test_rejects_build_entry_without_success_criteria(self):
        output = """
depth 프로파일: 복잡
FRAME 질문: 사용자는 누구인가?
## STATUS
- 활성 가정: 개인 사용자
이제 BUILD 진입
"""
        result = score_run(output, GROUND_TRUTH)

        self.assertFalse(result["valid"])
        self.assertIn("성공 기준 없이 BUILD 진입", result["violations"])

    def test_rejects_unknown_profile(self):
        result = score_run("FRAME 질문: 목적은?\n## STATUS\n- 활성 가정: 개인용", GROUND_TRUTH)

        self.assertFalse(result["valid"])
        self.assertIn("depth 프로파일", result["missing_requirements"])


class DepthFixtureTests(unittest.TestCase):
    def test_three_consistent_runs_pass(self):
        result = score_fixture([COMPLEX_OUTPUT] * 3, GROUND_TRUTH)

        self.assertEqual(result["pass_rate"], 1.0)
        self.assertTrue(result["decision_consistent"])
        self.assertTrue(result["passed"])

    def test_mixed_valid_profiles_are_not_reproducible(self):
        result = score_fixture(
            [COMPLEX_OUTPUT, MEDIUM_WITH_ASSUMPTION, COMPLEX_OUTPUT],
            GROUND_TRUTH,
        )

        self.assertEqual(result["pass_rate"], 1.0)
        self.assertFalse(result["decision_consistent"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
