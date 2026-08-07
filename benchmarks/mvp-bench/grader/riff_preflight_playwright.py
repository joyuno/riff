#!/usr/bin/env python3
"""Live Playwright checks for the Riff synthetic preflight apps.

구현에 결합된 셀렉터(#id, .class, 정확한 라벨 문자열) 대신
'의미'(접근성 라벨·placeholder·name·id)로 컨트롤을 찾고,
판정은 렌더된 결과(본문 텍스트·계산 결과·새로고침 후 상태)로 한다.
그래야 riff / GSD / gstack 등 어떤 하네스가 만든 앱이든 같은 자로 잰다.
"""

from __future__ import annotations

import json
import re
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


# --------------------------------------------------------------------------
# 구현 독립 로케이터 — 의미로 찾는다. 못 찾으면 None (크래시 대신 실패로 흐른다).
# --------------------------------------------------------------------------

_SHOWN = "const shown = el => !!(el.offsetParent || el.getClientRects().length);"

_MEANING = """
  const kind = el => el.tagName === 'INPUT'
    ? (el.getAttribute('type') || 'text').toLowerCase()
    : el.tagName.toLowerCase();
  const meaning = el => [
    el.labels ? [...el.labels].map(l => l.textContent).join(' ') : '',
    el.closest('label') ? el.closest('label').textContent : '',
    el.getAttribute('aria-label') || '',
    el.getAttribute('placeholder') || '',
    el.getAttribute('name') || '',
    el.id || '',
    el.getAttribute('title') || '',
  ].join(' ');
"""

FIND_FIELD_JS = """
(root, [pattern, kinds, exclude]) => {
  %s%s
  const re = new RegExp(pattern, 'i');
  const want = kinds ? kinds.split(',') : null;
  const pool = [...root.querySelectorAll('input, textarea, select')]
    .filter(shown)
    .filter(el => !want || want.includes(kind(el)))
    .filter(el => !exclude || !exclude.contains(el));
  return pool.find(el => re.test(meaning(el))) || null;
}
""" % (_SHOWN, _MEANING)

# 반복되는 항목 행(line item)을 모두 채운다. 빈 행을 남기면 앱이 저장을 막는다.
FILL_ALL_JS = """
(root, [pattern, value]) => {
  %s%s
  const re = new RegExp(pattern, 'i');
  let filled = 0;
  for (const el of root.querySelectorAll('input, textarea')) {
    if (!shown(el) || !re.test(meaning(el))) continue;
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    filled += 1;
  }
  return filled;
}
""" % (_SHOWN, _MEANING)

# 폼 제출은 텍스트보다 type=submit을 우선한다("+ 항목 추가" 같은 보조 버튼과 헷갈리지 않게).
SUBMIT_JS = """
(form, pattern) => {
  %s
  const re = new RegExp(pattern, 'i');
  const label = b => (b.innerText || b.value || '').trim();
  const buttons = [...form.querySelectorAll(
    'button, input[type=submit], input[type=button], [role=button]')].filter(shown);
  const submits = buttons.filter(b => (b.tagName === 'BUTTON'
    ? (b.getAttribute('type') || 'submit') : (b.getAttribute('type') || '')).toLowerCase() === 'submit');
  return submits.find(b => re.test(label(b))) || submits[0]
      || buttons.find(b => re.test(label(b))) || null;
}
""" % _SHOWN

FIND_BUTTON_JS = """
(root, pattern) => {
  %s
  const re = new RegExp(pattern, 'i');
  const nodes = [...root.querySelectorAll(
    'button, input[type=submit], input[type=button], [role=button]')];
  return nodes.find(el => shown(el) && re.test((el.innerText || el.value || '').trim())) || null;
}
""" % _SHOWN

FIND_FORM_JS = """
(root, pattern) => {
  %s
  const re = new RegExp(pattern, 'i');
  const forms = [...root.querySelectorAll('form')].filter(shown);
  const hit = forms.find(f => [...f.querySelectorAll('button, input[type=submit]')]
    .some(b => shown(b) && re.test((b.innerText || b.value || '').trim())));
  return hit || forms[0] || null;
}
""" % _SHOWN

FILL_BLANKS_JS = """
(form, today) => {
  %s
  for (const el of form.querySelectorAll('input, textarea, select')) {
    if (!shown(el) || !el.required || el.value) continue;
    const t = (el.getAttribute('type') || 'text').toLowerCase();
    if (t === 'checkbox' || t === 'radio') { el.checked = true; }
    else {
      el.value = t === 'number' ? '1' : t === 'date' ? today : t === 'time' ? '10:00'
        : t === 'tel' ? '010-0000-0000' : t === 'email' ? 'check@example.com' : '검수';
    }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
}
""" % _SHOWN

# 같은 부모 아래 같은 모양으로 반복되는, 내용 있는 요소의 최대 개수 = "목록 아이템 수".
ITEM_COUNT_JS = """
() => {
  %s
  const groups = new Map();
  for (const el of document.querySelectorAll('body *')) {
    const p = el.parentElement;
    if (!p || !shown(el)) continue;
    if ((el.innerText || '').trim().length < 20) continue;
    const key = [p.tagName, p.className, el.tagName, el.className].join('|');
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  return Math.max(0, ...groups.values());
}
""" % _SHOWN

# 상태 워크플로 컨트롤: 옵션/버튼 텍스트가 상태 어휘와 맞는 것.
FIND_STATUS_JS = """
(root, pattern) => {
  %s
  const re = new RegExp(pattern, 'i');
  const sel = [...root.querySelectorAll('select')].filter(shown)
    .find(s => [...s.options].some(o => re.test(o.textContent)));
  if (sel) return sel;
  return [...root.querySelectorAll('button, [role=button]')].filter(shown)
    .find(b => re.test(b.innerText || '')) || null;
}
""" % _SHOWN


def body_of(page: Page):
    return page.evaluate_handle("document.body").as_element()


def body_text(page: Page) -> str:
    return page.locator("body").inner_text()


def field(root, pattern: str, kinds: str | None = None, exclude=None):
    """의미로 입력 컨트롤을 찾는다. 없으면 None."""
    return root.evaluate_handle(FIND_FIELD_JS, [pattern, kinds, exclude]).as_element()


def set_field(root, pattern: str, value: str, kinds: str | None = None) -> bool:
    element = field(root, pattern, kinds)
    if element is None:
        return False
    element.fill(value)
    return True


def fill_all(root, pattern: str, value: str) -> int:
    return root.evaluate(FILL_ALL_JS, [pattern, value])


def click_button(root, pattern: str) -> bool:
    element = root.evaluate_handle(FIND_BUTTON_JS, pattern).as_element()
    if element is None:
        return False
    element.click()
    return True


def submit_form(form, pattern: str) -> bool:
    element = form.evaluate_handle(SUBMIT_JS, pattern).as_element()
    if element is None:
        return False
    element.click()
    return True


SUBMIT_RE = r"저장|추가|등록|만들기|생성|분석|save|add|submit|create"
OPENER_RE = r"새 |새$|새로|신규|작성|만들기|추가|new|\+"


def form_of(page: Page, submit_pattern: str = SUBMIT_RE):
    """제출 버튼을 가진 보이는 폼. 다이얼로그에 숨어 있으면 여는 버튼을 한 번 누른다."""
    body = body_of(page)
    found = body.evaluate_handle(FIND_FORM_JS, submit_pattern).as_element()
    if found is None:
        click_button(body, OPENER_RE)
        page.wait_for_timeout(150)
        body = body_of(page)
        found = body.evaluate_handle(FIND_FORM_JS, submit_pattern).as_element()
    return found


def has_amount(text: str, value: int) -> bool:
    return f"{value:,}" in text or str(value) in text


def mobile_check(page: Page) -> dict:
    page.set_viewport_size({"width": 390, "height": 844})
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    return result("mobile-390", False, not overflow, f"horizontal overflow={overflow}")


def research_check(run: Path) -> dict:
    path = run / "RESEARCH.md"
    if not path.exists():
        return result("research-evidence", True, False, "RESEARCH.md missing")
    text = path.read_text()
    sources = text.count("http://") + text.count("https://")
    return result("research-evidence", True, sources > 0, f"source links={sources}")


# --------------------------------------------------------------------------
# A — 예약·노쇼 관리
# --------------------------------------------------------------------------

DATE_RE = r"날짜|일자|date"
CONFLICT_RE = r"겹|중복|충돌|이미|불가|conflict|overlap"


def salon_fill(page: Page, name: str, amount: str, day: str, start: str) -> bool:
    form = form_of(page)
    if form is None:
        return False
    body = body_of(page)
    # 목록 조회 날짜(폼 밖)와 예약 날짜(폼 안)가 나뉜 구현이 있어 둘 다 맞춘다.
    view_date = field(body, DATE_RE, "date", exclude=form)
    if view_date is not None:
        view_date.fill(day)
        form = form_of(page)
        if form is None:
            return False
    set_field(form, DATE_RE, day, "date")
    named = set_field(form, r"고객|이름|성함|client|customer", name, "text")
    set_field(form, r"연락처|전화|휴대|phone|tel", "010-1111-2222", "text,tel")
    set_field(form, r"시작|시간|time", start, "time")
    set_field(form, r"금액|가격|비용|요금|price|amount|cost", amount, "number")
    form.evaluate(FILL_BLANKS_JS, date.today().isoformat())
    clicked = submit_form(form, SUBMIT_RE)
    page.wait_for_timeout(120)
    return named and clicked


def grade_salon(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()
    future = (date.today() + timedelta(days=2)).isoformat()
    past = (date.today() - timedelta(days=2)).isoformat()

    filled = salon_fill(page, "검수고객", "45000", future, "11:00")
    created = filled and "검수고객" in body_text(page)

    # 45,000 + 30,000 = 75,000. 합계가 화면에 나타나야 "예상 매출이 계산된다".
    salon_fill(page, "둘째고객", "30000", future, "13:00")
    revenue_text = body_text(page)
    revenue_ok = created and has_amount(revenue_text, 75000)

    page.reload()
    persisted = "검수고객" in body_text(page)

    before = body_text(page)
    salon_fill(page, "셋째고객", "45000", future, "11:00")
    after = body_text(page)
    conflict = (
        "셋째고객" not in after
        and bool(re.search(CONFLICT_RE, after))
        and not re.search(CONFLICT_RE, before)
    )

    salon_fill(page, "영원고객", "0", future, "15:00")
    zero_blocked = "영원고객" not in body_text(page)

    salon_fill(page, "과거고객", "45000", past, "12:30")
    past_blocked = "과거고객" not in body_text(page)

    return [
        result("booking-create", True, created, "created customer visible"),
        result("booking-conflict", True, conflict, "overlap message visible"),
        result("expected-revenue", True, revenue_ok, "45,000+30,000 총액 75,000 표시 여부"),
        result("persistence", True, persisted, "customer retained after reload"),
        result("zero-price", False, zero_blocked, "0 price booking rejected"),
        result("past-date", False, past_blocked, "past booking rejected"),
        mobile_check(page),
        research_check(run),
    ]


# --------------------------------------------------------------------------
# B — 고객 리뷰 인사이트
# --------------------------------------------------------------------------

# 시드 리뷰는 감정/주제 어휘(긍정·부정·배송·포장·품질·사이즈)를 일부러 쓰지 않는다.
# 그 단어가 화면에 나오면 앱이 분류한 결과지, 우리가 붙여넣은 문장이 아니다.
# 상품을 둘로 나눠야 필터가 실제로 걸러내는지 확인할 수 있다.
REVIEW_SEEDS = [
    (
        "검수상품가",
        "★☆☆☆☆ 박스가 찌그러진 채로 왔고 제품도 깨져 있었어요. 환불해주세요.\n\n"
        "★★★★★ 생각보다 훨씬 빨리 도착했어요. 잘 쓰고 있습니다.",
    ),
    (
        "검수상품나",
        "★★☆☆☆ 옷이 생각보다 작게 나왔네요. 교환 문의드립니다.\n\n"
        "★★☆☆☆ 며칠째 오지 않아서 문의했더니 그제서야 출발했다고 합니다.",
    ),
]
STATUS_RE = r"처리|검토|반영|상태|status"
FILTER_RE = r"주제|감정|카테고리|분류|필터|상품|검색|filter|theme|sentiment|search|category"


def seed_reviews(page: Page) -> bool:
    """리뷰 입력이 있는 구현이면 예시 리뷰를 넣어 준다(붙여넣기형 앱 대응)."""
    seeded = False
    for product, reviews in REVIEW_SEEDS:
        form = form_of(page)
        if form is None:
            break
        box = field(form, r".", "textarea")
        if box is None:
            break
        box.fill(reviews)
        set_field(form, r"상품|제품|product|품목", product, "text")
        form.evaluate(FILL_BLANKS_JS, date.today().isoformat())
        submit_form(form, SUBMIT_RE)
        page.wait_for_timeout(200)
        seeded = True
    return seeded


def grade_reviews(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()
    seed_reviews(page)

    items = page.evaluate(ITEM_COUNT_JS)
    text = body_text(page)
    sentiment = bool(
        re.search(r"긍정|positive", text)
        and re.search(r"부정|negative", text)
        and re.search(r"배송|포장|품질|사이즈", text)
    )

    body = body_of(page)
    review_form = form_of(page)
    filter_control = field(body, FILTER_RE, "select", exclude=review_form)
    filtered = False
    if filter_control is not None:
        baseline_text = body_text(page)
        options = filter_control.evaluate("el => el.options.length")
        for index in range(1, options):
            filter_control.select_option(index=index)
            page.wait_for_timeout(120)
            if body_text(page) != baseline_text:
                filtered = True
                break
        filter_control.select_option(index=0)
        page.wait_for_timeout(120)

    status_control = body_of(page).evaluate_handle(FIND_STATUS_JS, STATUS_RE).as_element()
    has_status = status_control is not None

    status_persisted = False
    if has_status and status_control.evaluate("el => el.tagName") == "SELECT":
        options = status_control.evaluate("el => [...el.options].map(o => o.value)")
        target = options[-1]
        status_control.select_option(value=target)
        page.wait_for_timeout(150)
        page.reload()
        page.wait_for_timeout(150)
        again = body_of(page).evaluate_handle(FIND_STATUS_JS, STATUS_RE).as_element()
        status_persisted = again is not None and again.evaluate("el => el.value") == target

    return [
        result("fixture-reviews", True, items >= 3, f"review items visible={items}"),
        result("sentiment-theme", True, sentiment, "sentiment and theme text visible"),
        result("filters", True, filtered, f"filter control re-rendered the list={filtered}"),
        result("processing-status", True, has_status, "workflow status options present"),
        result("summary", True, bool(re.search(r"전체 리뷰|평균|요약|건수|summary", text)), "review summary visible"),
        result("persistence", True, status_persisted, "status persistence requires a status control"),
        mobile_check(page),
        research_check(run),
    ]


# --------------------------------------------------------------------------
# C — 견적·고객 진행 관리
# --------------------------------------------------------------------------

QTY_RE = r"수량|개수|qty|quantity"
UNIT_RE = r"단가|개당|건당|unit"


def grade_quotes(page: Page, url: str, run: Path) -> list[dict]:
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()

    form = form_of(page)
    if form is None:
        checks = [result(name, True, False, "quote form not found") for name in
                  ("line-items", "vat-total", "status-change", "search-filter",
                   "revenue-summary", "persistence", "print-view")]
        return checks + [mobile_check(page), research_check(run)]

    # 항목 행이 버튼으로 추가되는 구현이면 한 번 눌러 준다.
    if field(form, QTY_RE) is None:
        click_button(form, r"항목|품목|줄|line|item")
        page.wait_for_timeout(120)
        form = form_of(page)

    qty = field(form, QTY_RE)
    unit = field(form, UNIT_RE)
    has_items = qty is not None and unit is not None

    set_field(form, r"고객|업체|회사|client|customer", "검수회사", "text")
    set_field(form, r"작업|프로젝트|제목|project|title", "검수 작업", "text")
    rows = 0
    if has_items:
        # 빈 항목 행이 남으면 저장이 막히므로 보이는 행을 전부 채운다.
        fill_all(form, r"품목|항목|설명|내용|description|item", "검수항목")
        rows = min(fill_all(form, QTY_RE, "2"), fill_all(form, UNIT_RE, "50000"))
    else:
        set_field(form, r"금액|가격|price|amount", "100000", "number")
    form.evaluate(FILL_BLANKS_JS, date.today().isoformat())
    submit_form(form, SUBMIT_RE)
    page.wait_for_timeout(200)

    text = body_text(page)
    supply = rows * 2 * 50000  # 행당 수량 2 × 단가 50,000
    vat_words = bool(re.search(r"부가세|부가가치세|vat", text, re.I) and re.search(r"공급가|공급 가액|supply", text))
    vat_ok = (
        has_items
        and supply > 0
        and vat_words
        and has_amount(text, supply + supply // 10)
        and has_amount(text, supply // 10)
    )

    statuses = [
        r"초안|작성중|작성 중|임시|draft",
        r"발송|보냄|전송|sent",
        r"승인|수락|approved",
        r"거절|반려|rejected",
    ]
    status_ok = all(re.search(pattern, text, re.I) for pattern in statuses)

    body = body_of(page)
    open_form = form_of(page)
    # 행별 상태 편집 select와 구분하려고 '검색/필터' 어휘로만 찾는다.
    search_control = field(body, r"검색|찾기|필터|조회|search|filter|query", None, exclude=open_form)
    has_filter = search_control is not None or page.get_by_role("searchbox").count() > 0

    revenue_ok = bool(re.search(r"예상 매출|expected", text) and re.search(r"승인|approved", text))

    has_print = page.evaluate(
        """[...document.styleSheets].some(s => {
             try { return [...s.cssRules].some(r => r.media && r.media.mediaText.includes('print')) }
             catch { return false }
           }) || [...document.querySelectorAll('link[media]')].some(l => l.media.includes('print'))"""
    )

    page.reload()
    persisted = "검수회사" in body_text(page)

    return [
        result("line-items", True, has_items, "quantity and unit-price inputs present"),
        result("vat-total", True, vat_ok, "supply, VAT and total visible"),
        result("status-change", True, status_ok, "four statuses present"),
        result("search-filter", True, has_filter, "customer or status filter present"),
        result("revenue-summary", True, revenue_ok, "expected and approved revenue visible"),
        result("persistence", True, persisted, "quote retained after reload"),
        result("print-view", True, has_print, "print media rule present"),
        mobile_check(page),
        research_check(run),
    ]


def app_dir(root: Path, name: str) -> Path:
    """앱은 <run>/app/에 두는 것이 규약이나, 초기 run은 루트에 둔 것이 있어 자동 판별한다."""
    candidate = root / name / "app"
    return candidate if (candidate / "index.html").exists() else root / name


def main() -> None:
    import sys

    # --root <dir>로 다른 실행 세트(예: runs-v2)를 채점할 수 있다. 결과는 <root>/../results-<이름>/.
    runs = RUNS
    results = RESULTS
    if "--root" in sys.argv:
        runs = Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
        results = runs.parent / f"results-{runs.name}"
        results.mkdir(parents=True, exist_ok=True)

    jobs = {
        "a-salon": (app_dir(runs, "a-salon"), grade_salon),
        "b-reviews": (app_dir(runs, "b-reviews"), grade_reviews),
        "c-quotes": (app_dir(runs, "c-quotes"), grade_quotes),
    }
    output = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for name, (directory, grader) in jobs.items():
                with serve(directory) as url:
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    try:
                        checks = grader(page, url, runs / name)
                    finally:
                        page.close()
                output[name] = checks
                (results / f"{name}.playwright.json").write_text(
                    json.dumps(checks, ensure_ascii=False, indent=2) + "\n"
                )
        finally:
            browser.close()
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
