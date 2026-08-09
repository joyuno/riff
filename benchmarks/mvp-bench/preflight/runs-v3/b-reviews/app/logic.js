// 순수 로직만 담는다 — DOM 의존 없음 (A-001, A-002, A-003, A-004, A-006, A-007 근거)
// 브라우저(<script>)에서는 window.Logic, Node(test.js)에서는 require()로 동일하게 쓴다.
(function (root, factory) {
  if (typeof module !== "undefined" && module.exports) {
    module.exports = factory();
  } else {
    root.Logic = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  var CATEGORIES = ["배송", "포장", "품질", "사이즈", "고객응대"];

  // A-007: 전화번호(하이픈 유무 모두)·이메일을 화면 표시용으로 마스킹한다. 원본은 저장소에 그대로 둔다.
  function maskPII(text) {
    if (!text) return text;
    var masked = text.replace(
      /(01[016789])[-.\s]?(\d{3,4})[-.\s]?(\d{4})/g,
      function (m, p1, p2, p3) {
        return p1 + "-" + "*".repeat(p2.length) + "-" + p3;
      }
    );
    masked = masked.replace(
      /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
      "****@****"
    );
    return masked;
  }

  function isNegative(rating) {
    return rating <= 2;
  }

  // A-003: 미확인 우선 → 별점 낮은 순 → 최신순
  function sortReviews(reviews) {
    return reviews.slice().sort(function (a, b) {
      if (a.status !== b.status) return a.status === "unconfirmed" ? -1 : 1;
      if (a.rating !== b.rating) return a.rating - b.rating;
      return new Date(b.date) - new Date(a.date);
    });
  }

  // A-003: 카테고리별 건수 요약 + 가장 시급한 카테고리(부정+미확인 합 최다)
  function summarize(reviews) {
    var byCategory = {};
    CATEGORIES.forEach(function (c) {
      byCategory[c] = { total: 0, negative: 0, unconfirmed: 0 };
    });
    reviews
      .filter(function (r) {
        return !r.deleted;
      })
      .forEach(function (r) {
        var c = byCategory[r.category];
        if (!c) return;
        c.total++;
        if (isNegative(r.rating)) c.negative++;
        if (r.status === "unconfirmed") c.unconfirmed++;
      });
    var mostUrgent = null;
    var maxScore = 0;
    CATEGORIES.forEach(function (c) {
      var score = byCategory[c].negative + byCategory[c].unconfirmed;
      if (score > maxScore) {
        maxScore = score;
        mostUrgent = c;
      }
    });
    return { byCategory: byCategory, mostUrgent: mostUrgent };
  }

  // A-004: 카테고리·상태·텍스트 필터 (삭제된 리뷰는 항상 제외)
  function filterReviews(reviews, filters) {
    filters = filters || {};
    return reviews.filter(function (r) {
      if (r.deleted) return false;
      if (filters.category && filters.category !== "all" && r.category !== filters.category)
        return false;
      if (filters.status && filters.status !== "all" && r.status !== filters.status)
        return false;
      if (filters.query) {
        var q = filters.query.toLowerCase();
        if (r.content.toLowerCase().indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  return {
    CATEGORIES: CATEGORIES,
    maskPII: maskPII,
    isNegative: isNegative,
    sortReviews: sortReviews,
    summarize: summarize,
    filterReviews: filterReviews,
  };
});
