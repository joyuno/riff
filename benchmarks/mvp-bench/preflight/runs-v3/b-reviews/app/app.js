(function () {
  var STORAGE_KEY = "shop_reviews_v1"; // A-005: localStorage에 저장해 새로고침 후에도 유지

  function loadReviews() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveReviews(reviews) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reviews));
  }

  var reviews = loadReviews();

  var els = {
    summaryGrid: document.getElementById("summary-grid"),
    urgentBanner: document.getElementById("urgent-banner"),
    form: document.getElementById("review-form"),
    fRating: document.getElementById("f-rating"),
    fCategory: document.getElementById("f-category"),
    fDate: document.getElementById("f-date"),
    fContent: document.getElementById("f-content"),
    filterCategory: document.getElementById("filter-category"),
    filterStatus: document.getElementById("filter-status"),
    filterQuery: document.getElementById("filter-query"),
    reviewList: document.getElementById("review-list"),
    emptyMsg: document.getElementById("empty-msg"),
    toggleTrash: document.getElementById("toggle-trash"),
    trashList: document.getElementById("trash-list"),
  };

  function populateCategorySelects() {
    Logic.CATEGORIES.forEach(function (c) {
      var opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      els.fCategory.appendChild(opt);
    });
    var allOpt = document.createElement("option");
    allOpt.value = "all";
    allOpt.textContent = "전체";
    els.filterCategory.appendChild(allOpt);
    Logic.CATEGORIES.forEach(function (c) {
      var opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      els.filterCategory.appendChild(opt);
    });
  }

  function genId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  // A-003: 카테고리별 요약 + 가장 시급한 카테고리 강조
  function renderSummary() {
    var summary = Logic.summarize(reviews);
    els.summaryGrid.innerHTML = "";
    Logic.CATEGORIES.forEach(function (c) {
      var s = summary.byCategory[c];
      var cell = document.createElement("div");
      cell.className = "summary-cell";
      cell.innerHTML =
        '<div class="cat-name">' + c + "</div>" +
        '<div class="cat-total">' + s.total + "건</div>" +
        '<div class="cat-negative">부정 ' + s.negative + " · 미확인 " + s.unconfirmed + "</div>";
      els.summaryGrid.appendChild(cell);
    });
    if (summary.mostUrgent) {
      els.urgentBanner.hidden = false;
      els.urgentBanner.textContent = "가장 시급한 카테고리: " + summary.mostUrgent;
    } else {
      els.urgentBanner.hidden = true;
    }
  }

  function reviewItemHtml(r, opts) {
    opts = opts || {};
    var statusLabel = r.status === "unconfirmed" ? "미확인" : "확인함";
    var actionsHtml;
    if (opts.trashed) {
      actionsHtml =
        '<button type="button" class="restore-btn" data-action="restore" data-id="' + r.id + '">복구</button>';
    } else {
      var toggleLabel = r.status === "unconfirmed" ? "확인함으로 표시" : "미확인으로 되돌리기";
      actionsHtml =
        '<button type="button" data-action="toggle-status" data-id="' + r.id + '">' + toggleLabel + "</button>" +
        '<button type="button" class="delete-btn" data-action="delete" data-id="' + r.id + '">삭제</button>';
    }
    return (
      '<li class="review-item ' + r.status + '">' +
      '<div class="review-top">' +
      '<span class="badge">' + r.category + "</span>" +
      '<span class="badge">' + "★".repeat(r.rating) + "☆".repeat(5 - r.rating) + "</span>" +
      '<span class="badge status-' + r.status + '">' + statusLabel + "</span>" +
      "</div>" +
      '<div class="review-content">' + escapeHtml(Logic.maskPII(r.content)) + "</div>" +
      '<div class="review-meta">' + r.date + "</div>" +
      '<div class="review-actions">' + actionsHtml + "</div>" +
      "</li>"
    );
  }

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  // A-004: 필터(카테고리/상태/검색어) 적용 + A-003 정렬
  function renderList() {
    var filters = {
      category: els.filterCategory.value,
      status: els.filterStatus.value,
      query: els.filterQuery.value.trim(),
    };
    var filtered = Logic.sortReviews(Logic.filterReviews(reviews, filters));
    els.reviewList.innerHTML = filtered.map(function (r) { return reviewItemHtml(r); }).join("");
    els.emptyMsg.hidden = filtered.length !== 0;
  }

  // A-006: 삭제된 리뷰 목록(복구 가능)
  function renderTrash() {
    var trashed = reviews.filter(function (r) { return r.deleted; });
    els.trashList.innerHTML = trashed
      .map(function (r) { return reviewItemHtml(r, { trashed: true }); })
      .join("");
    if (trashed.length === 0) {
      els.trashList.innerHTML = '<li class="empty-msg" style="list-style:none;">삭제된 리뷰가 없습니다.</li>';
    }
  }

  function renderAll() {
    renderSummary();
    renderList();
    renderTrash();
  }

  // A-001: 리뷰 추가
  els.form.addEventListener("submit", function (e) {
    e.preventDefault();
    reviews.push({
      id: genId(),
      rating: Number(els.fRating.value),
      category: els.fCategory.value,
      content: els.fContent.value.trim(),
      date: els.fDate.value,
      status: "unconfirmed", // A-002: 기본 상태는 미확인
      deleted: false,
    });
    saveReviews(reviews);
    els.form.reset();
    els.fDate.value = todayStr();
    els.fRating.value = "3";
    renderAll();
  });

  // A-002/A-006: 상태 토글, 삭제(soft delete), 복구 — 이벤트 위임
  function handleListClick(e) {
    var btn = e.target.closest("button[data-action]");
    if (!btn) return;
    var id = btn.getAttribute("data-id");
    var review = reviews.find(function (r) { return r.id === id; });
    if (!review) return;
    var action = btn.getAttribute("data-action");
    if (action === "toggle-status") {
      review.status = review.status === "unconfirmed" ? "confirmed" : "unconfirmed";
    } else if (action === "delete") {
      review.deleted = true;
    } else if (action === "restore") {
      review.deleted = false;
    }
    saveReviews(reviews);
    renderAll();
  }
  els.reviewList.addEventListener("click", handleListClick);
  els.trashList.addEventListener("click", handleListClick);

  // A-004: 필터 변경 시 목록 갱신
  [els.filterCategory, els.filterStatus].forEach(function (el) {
    el.addEventListener("change", renderList);
  });
  els.filterQuery.addEventListener("input", renderList);

  els.toggleTrash.addEventListener("click", function () {
    var willShow = els.trashList.hidden;
    els.trashList.hidden = !willShow;
    els.toggleTrash.textContent = willShow ? "삭제된 리뷰 숨기기" : "삭제된 리뷰 보기";
  });

  function todayStr() {
    var d = new Date();
    var mm = String(d.getMonth() + 1).padStart(2, "0");
    var dd = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + mm + "-" + dd;
  }

  populateCategorySelects();
  els.filterCategory.value = "all";
  els.fDate.value = todayStr();
  renderAll();
})();
