// Tier 2 실행 가능 체크 — node app/logic.test.js
const assert = require('assert');
const { calcAmounts, isValidAmount, sumApproved, formatCurrency } = require('./app.js');

// A-002: 부가세 별도 — 공급가 100,000 -> 부가세 10,000, 합계 110,000
{
  const r = calcAmounts(100000, 'exclusive');
  assert.deepStrictEqual(r, { supply: 100000, vat: 10000, total: 110000 });
}

// A-002: 부가세 포함 — 합계 110,000 입력 -> 공급가 100,000, 부가세 10,000 역산
{
  const r = calcAmounts(110000, 'inclusive');
  assert.deepStrictEqual(r, { supply: 100000, vat: 10000, total: 110000 });
}

// A-006: 잘못된 금액 거부
assert.strictEqual(isValidAmount(0), false);
assert.strictEqual(isValidAmount(-5), false);
assert.strictEqual(isValidAmount(NaN), false);
assert.strictEqual(isValidAmount(50000), true);

// A-008: 승인 + 보관되지 않은 견적만 합산
{
  const quotes = [
    { status: 'approved', archived: false, total: 100000 },
    { status: 'approved', archived: true, total: 999999 }, // 보관됨 -> 제외
    { status: 'sent', archived: false, total: 50000 }, // 미승인 -> 제외
    { status: 'approved', archived: false, total: 50000 },
  ];
  assert.strictEqual(sumApproved(quotes), 150000);
}

// 통화 포맷
assert.strictEqual(formatCurrency(110000), '110,000원');

console.log('logic.test.js: 전체 통과');
