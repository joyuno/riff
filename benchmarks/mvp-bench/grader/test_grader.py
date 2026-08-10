#!/usr/bin/env python3
"""채점기가 정말 판별하는지 검증한다.

fixtures/pass — 모든 체크를 통과하도록 의도한 최소 앱. critical 실패 0건이어야 한다.
fixtures/fail — pass에서 critical 요건을 하나씩만 제거한 변형. 그 체크 하나만 실패해야 한다.

채점 로직은 `riff_preflight_playwright`의 grade_* 함수를 그대로 호출한다(파일 출력만 건너뛴다).
브라우저를 못 쓰는 환경에서는 전체 skip.

실행: cd benchmarks/mvp-bench/grader && python3 -m unittest test_grader -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

GRADER_DIR = Path(__file__).resolve().parent
FIXTURES = GRADER_DIR / "fixtures"
sys.path.insert(0, str(GRADER_DIR))

# 채점기 import는 try 밖 — 채점기가 깨지면 skip이 아니라 즉시 실패해야 한다.
# (hard gate가 조용히 통과처럼 보이는 것을 막는다)
import riff_preflight_playwright as grader

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as _playwright:
        _blocker = None if Path(_playwright.chromium.executable_path).exists() else "Chromium 실행 파일 없음"
except Exception as exc:  # playwright 미설치·브라우저 미설치 환경
    _blocker = f"{type(exc).__name__}: {exc}"

# fail fixture가 의도적으로 깨뜨린 체크 id (파일 상단 주석과 일치해야 한다)
BROKEN = {
    "a-salon": "booking-conflict",
    "b-reviews": "persistence",
    "c-quotes": "vat-total",
}


@unittest.skipUnless(_blocker is None, f"Playwright Chromium 불가: {_blocker}")
class GraderDiscriminatesFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.graders = {
            "a-salon": grader.grade_salon,
            "b-reviews": grader.grade_reviews,
            "c-quotes": grader.grade_quotes,
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

    def grade(self, variant: str, task: str) -> dict[str, dict]:
        run = FIXTURES / variant / task
        with grader.serve(grader.app_dir(FIXTURES / variant, task)) as url:
            page = self.browser.new_page(viewport={"width": 1280, "height": 900})
            try:
                checks = self.graders[task](page, url, run)
            finally:
                page.close()
        self.assertTrue(checks, f"{variant}/{task}: 체크 결과가 비어 있다")
        return {check["id"]: check for check in checks}

    @staticmethod
    def critical_failures(checks: dict[str, dict]) -> list[str]:
        return sorted(i for i, c in checks.items() if c["critical"] and not c["passed"])

    def test_pass_fixtures_have_no_critical_failure(self) -> None:
        for task in BROKEN:
            with self.subTest(task=task):
                checks = self.grade("pass", task)
                self.assertEqual([], self.critical_failures(checks))

    def test_fail_fixtures_break_only_the_intended_check(self) -> None:
        for task, broken in BROKEN.items():
            with self.subTest(task=task, broken=broken):
                checks = self.grade("fail", task)
                self.assertIn(broken, checks)
                self.assertFalse(checks[broken]["passed"], f"{task}: {broken}가 실패하지 않았다")
                self.assertEqual([broken], self.critical_failures(checks))


if __name__ == "__main__":
    unittest.main()
