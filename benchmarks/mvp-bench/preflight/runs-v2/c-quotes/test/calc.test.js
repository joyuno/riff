// PROVE Tier 2 self-check — 계산 로직(A-001, A-003, A-009)이 깨지면 여기서 바로 잡힌다.
// 실행: node test/calc.test.js
const assert = require('assert');
const calc = require('../app/calc.js');

// A-001: 항목 금액 = 수량 × 단가, 합계 = 항목 합
assert.strictEqual(calc.lineTotal(2, 50000), 100000, 'lineTotal 계산 오류');
assert.strictEqual(
  calc.quoteTotal([
    { qty: 2, price: 50000 },
    { qty: 1, price: 30000 },
  ]),
  130000,
  'quoteTotal 합계 오류'
);

// A-009: 잘못된 입력 거부
assert.strictEqual(calc.validateLineItem(2, 50000).valid, true, '정상 입력이 거부됨');
assert.strictEqual(calc.validateLineItem('abc', 50000).valid, false, '숫자 아닌 값이 통과함');
assert.strictEqual(calc.validateLineItem(-1, 50000).valid, false, '음수 수량이 통과함');
assert.strictEqual(calc.validateLineItem(2, 0).valid, false, '0원 단가가 통과함');

// A-003: 예상 매출 = 승인됨 상태 견적 합계만
const quotes = [
  { status: 'approved', items: [{ qty: 1, price: 100000 }] },
  { status: 'sent', items: [{ qty: 1, price: 999999 }] },
  { status: 'approved', items: [{ qty: 2, price: 50000 }] },
];
assert.strictEqual(calc.approvedTotal(quotes), 200000, '승인됨 상태만 합산해야 함');

// A-006: 유효기간 라벨
assert.strictEqual(calc.validUntilLabel('2026-08-07', 0), '유효기간 미지정', '0일 처리 오류');
assert.strictEqual(
  calc.validUntilLabel('2026-08-07', 14),
  '2026-08-21까지 유효 (발행일로부터 14일)',
  '유효기간 계산 오류'
);

// 통화 포맷
assert.strictEqual(calc.formatWon(130000), '130,000원', '통화 포맷 오류');

console.log('calc.test.js: 9/9 통과');
