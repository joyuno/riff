// 리뷰 인사이트 — 키워드 기반 분류 + 우선순위 (A-001~A-005)
// ponytail: 규칙 기반 키워드 매칭. 오분류가 잦아지면(항체 2회+) 사전 확장 또는 형태소 분석기 도입 검토.

const STORAGE_KEY = "reviewInsight:v1";

const CATEGORIES = {
  배송: ["배송", "택배", "도착", "지연", "늦게", "늦었", "발송"],
  포장: ["포장", "박스", "찌그러", "상자", "완충", "뽁뽁이"],
  품질: ["품질", "불량", "하자", "파손", "고장", "냄새", "재질", "변색", "터짐", "깨짐"],
  사이즈: ["사이즈", "치수", "크기", "작아", "커요", "작네", "헐렁", "타이트"],
  응대: ["응대", "상담", "답변", "문의", "불친절", "친절", "연락"],
};

const SEVERE_KEYWORDS = ["파손", "환불", "안전", "위험", "화상", "유해", "다침", "다쳤", "사고"];

function loadReviews() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveReviews(reviews) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reviews));
}

function categorize(body) {
  const hits = [];
  for (const [cat, keywords] of Object.entries(CATEGORIES)) {
    if (keywords.some((kw) => body.includes(kw))) hits.push(cat);
  }
  return hits;
}

function isSevere(body, rating) {
  if (rating === 1) return true;
  return SEVERE_KEYWORDS.some((kw) => body.includes(kw));
}

// "별점 ★☆☆☆☆ / 이OO / 2026.07.20\n본문..." 형태를 우선 인식하되,
// 별점 줄이 없으면 블록 전체를 본문으로 취급한다.
function parseBlock(block) {
  const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length === 0) return null;

  const starMatch = lines[0].match(/[★☆]{3,5}/);
  let meta = null;
  let rating = null;
  let bodyLines = lines;

  if (starMatch && lines.length > 1) {
    rating = (starMatch[0].match(/★/g) || []).length;
    meta = lines[0];
    bodyLines = lines.slice(1);
  }

  const body = bodyLines.join(" ").trim();
  if (!body) return null;

  let nickname = "";
  let date = "";
  if (meta) {
    const parts = meta.split("/").map((p) => p.trim());
    nickname = parts[1] || "";
    date = parts[2] || "";
  }

  return { rating, nickname, date, body };
}

function parseInput(product, rawText) {
  const blocks = rawText.split(/\n\s*\n/);
  return blocks
    .map(parseBlock)
    .filter(Boolean)
    .map((parsed) => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      product,
      body: parsed.body,
      rating: parsed.rating,
      nickname: parsed.nickname,
      date: parsed.date,
      categories: categorize(parsed.body),
      severe: isSevere(parsed.body, parsed.rating),
      createdAt: Date.now(),
    }));
}

function dedupeKey(review) {
  return `${review.product}::${review.body.replace(/\s+/g, "")}`;
}

function addReviews(newReviews) {
  const existing = loadReviews();
  const existingKeys = new Set(existing.map(dedupeKey));
  let addedCount = 0;
  let dupCount = 0;

  for (const review of newReviews) {
    const key = dedupeKey(review);
    if (existingKeys.has(key)) {
      dupCount++;
      continue;
    }
    existingKeys.add(key);
    existing.push(review);
    addedCount++;
  }

  saveReviews(existing);
  return { addedCount, dupCount };
}

function renderCategorySummary(reviews) {
  const list = document.getElementById("category-summary");
  const emptyNote = document.getElementById("empty-summary");
  list.innerHTML = "";

  if (reviews.length === 0) {
    emptyNote.style.display = "block";
    return;
  }
  emptyNote.style.display = "none";

  const counts = {};
  for (const cat of Object.keys(CATEGORIES)) counts[cat] = 0;
  let unclassified = 0;

  for (const r of reviews) {
    if (r.categories.length === 0) unclassified++;
    for (const cat of r.categories) counts[cat]++;
  }

  for (const [cat, count] of Object.entries(counts)) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="count">${count}</span><span class="label">${cat}</span>`;
    list.appendChild(li);
  }

  const li = document.createElement("li");
  li.innerHTML = `<span class="count">${unclassified}</span><span class="label">미분류</span>`;
  list.appendChild(li);
}

function renderPriorityTable(reviews) {
  const tbody = document.querySelector("#priority-table tbody");
  tbody.innerHTML = "";

  const byProduct = {};
  for (const r of reviews) {
    if (!byProduct[r.product]) {
      byProduct[r.product] = { severeCount: 0, issueCount: 0, categoryCounts: {} };
    }
    const entry = byProduct[r.product];
    if (r.severe) entry.severeCount++;
    if (r.categories.length > 0) entry.issueCount++;
    for (const cat of r.categories) {
      entry.categoryCounts[cat] = (entry.categoryCounts[cat] || 0) + 1;
    }
  }

  const rows = Object.entries(byProduct)
    .map(([product, data]) => {
      const mainCategory =
        Object.entries(data.categoryCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "-";
      return { product, ...data, mainCategory };
    })
    .sort((a, b) => b.severeCount - a.severeCount || b.issueCount - a.issueCount);

  rows.forEach((row, idx) => {
    const tr = document.createElement("tr");
    if (row.severeCount > 0) tr.classList.add("severe-row");
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${escapeHtml(row.product)}</td>
      <td>${row.severeCount > 0 ? row.severeCount + '<span class="badge-severe">심각</span>' : "-"}</td>
      <td>${row.issueCount}</td>
      <td>${row.mainCategory}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSevereList(reviews) {
  const list = document.getElementById("severe-list");
  const emptyNote = document.getElementById("empty-severe");
  list.innerHTML = "";

  const severeReviews = reviews.filter((r) => r.severe).sort((a, b) => b.createdAt - a.createdAt);

  if (severeReviews.length === 0) {
    emptyNote.style.display = "block";
    return;
  }
  emptyNote.style.display = "none";

  for (const r of severeReviews) {
    const li = document.createElement("li");
    const ratingText = r.rating ? `★${r.rating}` : "별점 없음";
    li.innerHTML = `
      <div class="review-meta">${escapeHtml(r.product)} · ${ratingText} · ${escapeHtml(r.nickname || "")} ${escapeHtml(r.date || "")}</div>
      <div>${escapeHtml(r.body)}</div>
    `;
    list.appendChild(li);
  }
}

function renderProductFilter(reviews) {
  const select = document.getElementById("product-filter");
  const current = select.value;
  const products = [...new Set(reviews.map((r) => r.product))];

  select.innerHTML = '<option value="__all__">전체</option>';
  for (const p of products) {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    select.appendChild(opt);
  }
  if (products.includes(current)) select.value = current;
}

function renderRawList(reviews) {
  const list = document.getElementById("raw-list");
  const filter = document.getElementById("product-filter").value || "__all__";
  list.innerHTML = "";

  const filtered = filter === "__all__" ? reviews : reviews.filter((r) => r.product === filter);
  const sorted = [...filtered].sort((a, b) => b.createdAt - a.createdAt);

  for (const r of sorted) {
    const li = document.createElement("li");
    const ratingText = r.rating ? `★${r.rating}` : "별점 없음";
    const tags = r.categories.map((c) => `<span class="tag">${c}</span>`).join("") || "";
    li.innerHTML = `
      <div class="review-meta">${escapeHtml(r.product)} · ${ratingText} · ${escapeHtml(r.nickname || "")} ${escapeHtml(r.date || "")}</div>
      <div>${escapeHtml(r.body)}</div>
      <div>${tags}</div>
    `;
    list.appendChild(li);
  }
}

function renderAll() {
  const reviews = loadReviews();
  renderCategorySummary(reviews);
  renderPriorityTable(reviews);
  renderSevereList(reviews);
  renderProductFilter(reviews);
  renderRawList(reviews);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// 브라우저에서만 DOM을 연결한다 — Node의 PROVE 자가 점검(tests/test_app.js)에서는
// document가 없으므로 이 블록을 건너뛰고 위 순수 함수만 검증한다.
if (typeof document !== "undefined") {
  document.getElementById("review-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const productInput = document.getElementById("product-name");
    const textInput = document.getElementById("review-text");
    const product = productInput.value.trim();
    const rawText = textInput.value.trim();

    if (!product || !rawText) return;

    const parsed = parseInput(product, rawText);
    const { addedCount, dupCount } = addReviews(parsed);

    const status = document.getElementById("import-status");
    status.textContent = `${addedCount}건 추가${dupCount > 0 ? ` / 중복 ${dupCount}건 제외` : ""}`;

    productInput.value = "";
    textInput.value = "";
    renderAll();
  });

  document.getElementById("product-filter").addEventListener("change", () => {
    renderRawList(loadReviews());
  });

  document.getElementById("reset-all").addEventListener("click", () => {
    if (confirm("저장된 모든 리뷰를 삭제할까요? 되돌릴 수 없습니다.")) {
      localStorage.removeItem(STORAGE_KEY);
      document.getElementById("import-status").textContent = "";
      renderAll();
    }
  });

  renderAll();
}

if (typeof module !== "undefined") {
  module.exports = { categorize, isSevere, parseBlock, parseInput, dedupeKey, addReviews, loadReviews, saveReviews };
}
