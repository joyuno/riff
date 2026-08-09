// PROVE Tier 2 실행 가능 체크 — 프레임워크 없이 node app/test.js 로 실행한다.
// A-NNN 주석은 detail/acceptance/cycle-0.md의 동결 acceptance와 대응한다.
const assert = require("assert");
const Logic = require("./logic.js");

// A-007: 하이픈 있는/없는 전화번호, 이메일 마스킹
assert.strictEqual(Logic.maskPII("연락처 010-1234-5678 입니다"), "연락처 010-****-5678 입니다");
assert.strictEqual(Logic.maskPII("연락처 01012345678 입니다"), "연락처 010-****-5678 입니다");
assert.strictEqual(Logic.maskPII("메일은 foo@bar.com 로 주세요"), "메일은 ****@**** 로 주세요");
assert.strictEqual(Logic.maskPII("개인정보 없는 리뷰입니다"), "개인정보 없는 리뷰입니다");

// A-003: 정렬 — 미확인 우선 → 별점 낮은 순 → 최신순
const sorted = Logic.sortReviews([
  { id: 1, status: "confirmed", rating: 1, date: "2026-08-01" },
  { id: 2, status: "unconfirmed", rating: 5, date: "2026-08-02" },
  { id: 3, status: "unconfirmed", rating: 2, date: "2026-08-03" },
]);
assert.deepStrictEqual(sorted.map((r) => r.id), [3, 2, 1]);

// A-003: 카테고리 요약 + 가장 시급한 카테고리
const summary = Logic.summarize([
  { category: "배송", rating: 1, status: "unconfirmed", deleted: false },
  { category: "배송", rating: 5, status: "confirmed", deleted: false },
  { category: "포장", rating: 4, status: "confirmed", deleted: false },
  { category: "배송", rating: 2, status: "confirmed", deleted: true }, // 삭제됨 → 집계 제외
]);
assert.strictEqual(summary.byCategory["배송"].total, 2);
assert.strictEqual(summary.byCategory["배송"].negative, 1);
assert.strictEqual(summary.byCategory["배송"].unconfirmed, 1);
assert.strictEqual(summary.mostUrgent, "배송");

// A-004: 필터 — 카테고리/상태/텍스트, 삭제된 항목은 항상 제외
const pool = [
  { category: "배송", status: "unconfirmed", content: "너무 늦게 왔어요", deleted: false },
  { category: "포장", status: "confirmed", content: "박스가 찌그러짐", deleted: false },
  { category: "배송", status: "confirmed", content: "빨라요", deleted: true },
];
assert.strictEqual(Logic.filterReviews(pool, { category: "배송" }).length, 1);
assert.strictEqual(Logic.filterReviews(pool, { status: "confirmed" }).length, 1);
assert.strictEqual(Logic.filterReviews(pool, { query: "찌그러" }).length, 1);
assert.strictEqual(Logic.filterReviews(pool, {}).length, 2); // 삭제 1건 제외

console.log("OK - all logic.js checks passed");
