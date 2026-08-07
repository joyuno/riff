// calc.js — 순수 계산 로직만 담는다(DOM 없음).
// 브라우저(<script src="calc.js">)와 Node(test/calc.test.js) 양쪽에서 그대로 실행된다.
(function (root) {
  'use strict';

  function validateLineItem(qty, price) {
    var q = Number(qty);
    var p = Number(price);
    if (!Number.isFinite(q) || !Number.isFinite(p)) {
      return { valid: false, error: '수량과 단가는 숫자로 입력해주세요.' };
    }
    if (q <= 0 || p <= 0) {
      return { valid: false, error: '수량과 단가는 0보다 커야 해요.' };
    }
    return { valid: true, error: null };
  }

  function lineTotal(qty, price) {
    return Number(qty) * Number(price);
  }

  function quoteTotal(items) {
    return (items || []).reduce(function (sum, item) {
      return sum + lineTotal(item.qty, item.price);
    }, 0);
  }

  function approvedTotal(quotes) {
    return (quotes || [])
      .filter(function (q) {
        return q.status === 'approved';
      })
      .reduce(function (sum, q) {
        return sum + quoteTotal(q.items);
      }, 0);
  }

  function formatWon(amount) {
    return Math.round(amount || 0).toLocaleString('ko-KR') + '원';
  }

  function validUntilLabel(createdAt, validDays) {
    var days = Number(validDays);
    if (!days || days <= 0) return '유효기간 미지정';
    var created = new Date(createdAt);
    var until = new Date(created.getTime() + days * 24 * 60 * 60 * 1000);
    var y = until.getFullYear();
    var m = String(until.getMonth() + 1).padStart(2, '0');
    var d = String(until.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + d + '까지 유효 (발행일로부터 ' + days + '일)';
  }

  var calc = {
    validateLineItem: validateLineItem,
    lineTotal: lineTotal,
    quoteTotal: quoteTotal,
    approvedTotal: approvedTotal,
    formatWon: formatWon,
    validUntilLabel: validUntilLabel,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = calc;
  } else {
    root.calc = calc;
  }
})(typeof window !== 'undefined' ? window : globalThis);
