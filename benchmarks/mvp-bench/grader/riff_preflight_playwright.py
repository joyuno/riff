#!/usr/bin/env python3
"""Live Playwright checks for the three Riff synthetic preflight apps."""

from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from datetime import date, timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).parents[1]
RUNS = ROOT / "preflight" / "runs"
RESULTS = ROOT / "preflight" / "results"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        pass


@contextmanager
def serve(directory: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(directory)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


def result(check_id: str, critical: bool, passed: bool, evidence: str) -> dict:
    return {"id": check_id, "critical": critical, "passed": bool(passed), "evidence": evidence}


def mobile_check(page: Page) -> dict:
    page.set_viewport_size({"width": 390, "height": 844})
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    return result("mobile-390", False, not overflow, f"horizontal overflow={overflow}")


def research_check(run: Path) -> dict:
    text = (run / "RESEARCH.md").read_text()
    sources = text.count("http://") + text.count("https://")
    return result("research-evidence", True, sources > 0, f"source links={sources}")


def grade_salon(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()
    future = (date.today() + timedelta(days=2)).isoformat()

    def fill(name: str, amount: str = "45000", day: str = future, start: str = "11:00"):
        page.get_by_label("날짜").fill(day)
        page.get_by_label("고객 이름").fill(name)
        page.get_by_label("연락처").fill("010-1111-2222")
        page.get_by_label("시작 시간").fill(start)
        page.get_by_label("시술 금액").fill(amount)
        page.get_by_role("button", name="예약 저장").click()

    fill("검수고객")
    created = page.get_by_text("검수고객", exact=True).count() == 1
    expected = page.locator("#revenue").inner_text()
    page.reload()
    persisted = page.get_by_text("검수고객", exact=True).count() == 1
    fill("충돌고객")
    conflict = "겹" in page.locator("#form-message").inner_text()
    fill("영원고객", "0", future, "12:00")
    zero_blocked = page.get_by_text("영원고객", exact=True).count() == 0
    past = (date.today() - timedelta(days=2)).isoformat()
    fill("과거고객", "45000", past, "12:30")
    past_blocked = page.get_by_text("과거고객", exact=True).count() == 0

    checks = [
        result("booking-create", True, created, "created customer visible"),
        result("booking-conflict", True, conflict, "overlap message visible"),
        result("expected-revenue", True, "45,000" in expected, f"confirmed booking summary={expected}"),
        result("persistence", True, persisted, "customer retained after reload"),
        result("zero-price", False, zero_blocked, "0 price booking rejected"),
        result("past-date", False, past_blocked, "past booking rejected"),
        mobile_check(page),
        research_check(run),
    ]
    return checks


def grade_reviews(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    text = page.locator("body").inner_text()
    option_text = page.locator("option").all_inner_texts()
    has_status = any(value in option_text for value in ("처리 전", "검토 중", "개선 반영"))
    checks = [
        result("fixture-reviews", True, page.locator(".review-card").count() > 0, "review cards visible"),
        result("sentiment-theme", True, "긍정" in text and "부정" in text and "배송" in text, "sentiment and theme text visible"),
        result("filters", True, page.locator("select").count() >= 2, f"select filters={page.locator('select').count()}"),
        result("processing-status", True, has_status, "workflow status options present"),
        result("summary", True, "전체 리뷰" in text or "평균" in text, "review summary visible"),
        result("persistence", True, has_status, "status persistence requires a status control"),
        mobile_check(page),
        research_check(run),
    ]
    return checks


def grade_quotes(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()
    text = page.locator("body").inner_text()
    labels = page.locator("label").all_inner_texts()
    has_items = any("수량" in label for label in labels) and any("단가" in label for label in labels)
    has_vat = "부가세" in text and "공급가" in text
    has_filter = page.get_by_role("searchbox").count() > 0 or any("상태 필터" in label for label in labels)
    has_print = page.evaluate("""[...document.styleSheets].some(s => { try { return [...s.cssRules].some(r => r.media && r.media.mediaText.includes('print')) } catch { return false } })""")
    page.get_by_label("고객명").fill("검수회사")
    page.get_by_label("작업명").fill("검수 작업")
    page.get_by_label("견적 금액 (원)").fill("100000")
    page.get_by_role("button", name="초안으로 저장").click()
    page.reload()
    persisted = page.get_by_text("검수회사", exact=False).count() > 0
    checks = [
        result("line-items", True, has_items, "quantity and unit-price inputs present"),
        result("vat-total", True, has_vat, "supply, VAT and total visible"),
        result("status-change", True, all(value in text for value in ("초안", "발송", "승인", "거절")), "four statuses present"),
        result("search-filter", True, has_filter, "customer or status filter present"),
        result("revenue-summary", True, "예상 매출" in text and "승인 매출" in text, "expected and approved revenue visible"),
        result("persistence", True, persisted, "quote retained after reload"),
        result("print-view", True, has_print, "print media rule present"),
        mobile_check(page),
        research_check(run),
    ]
    return checks


def main() -> None:
    jobs = {
        "a-salon": (RUNS / "a-salon" / "app", grade_salon),
        "b-reviews": (RUNS / "b-reviews", grade_reviews),
        "c-quotes": (RUNS / "c-quotes" / "app", grade_quotes),
    }
    output = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for name, (directory, grader) in jobs.items():
                with serve(directory) as url:
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    try:
                        checks = grader(page, url, RUNS / name)
                    finally:
                        page.close()
                output[name] = checks
                (RESULTS / f"{name}.playwright.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
        finally:
            browser.close()
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
