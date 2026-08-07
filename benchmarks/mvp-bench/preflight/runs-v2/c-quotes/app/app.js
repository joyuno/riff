// app.js — 화면 로직 + localStorage 저장. 계산은 calc.js에 전부 위임한다.
(function () {
  'use strict';

  var STORAGE_KEY = 'cq_quotes_v1';
  var STATUSES = [
    { value: 'draft', label: '작성중' },
    { value: 'sent', label: '발송함' },
    { value: 'approved', label: '승인됨' },
    { value: 'hold', label: '보류' },
    { value: 'rejected', label: '거절됨' },
  ];

  function statusLabel(v) {
    var found = STATUSES.filter(function (s) { return s.value === v; })[0];
    return found ? found.label : v;
  }

  function loadQuotes() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveQuotes() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(quotes));
  }

  function makeId() {
    return 'q_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  var quotes = loadQuotes();
  var editingId = null;
  var previewConfirmHandler = null;

  // ---- DOM 참조 ----
  var approvedTotalEl = document.getElementById('approvedTotal');
  var quoteListEl = document.getElementById('quoteList');
  var emptyStateEl = document.getElementById('emptyState');

  var formDialog = document.getElementById('formDialog');
  var quoteForm = document.getElementById('quoteForm');
  var itemRowsEl = document.getElementById('itemRows');
  var formErrorEl = document.getElementById('formError');
  var formTotalEl = document.getElementById('formTotal');

  var previewDialog = document.getElementById('previewDialog');
  var previewContentEl = document.getElementById('previewContent');

  var historyDialog = document.getElementById('historyDialog');
  var historyListEl = document.getElementById('historyList');

  var printAreaEl = document.getElementById('printArea');

  // ---- 견적 텍스트(복사/인쇄/미리보기 공용) ----
  function buildQuoteText(q) {
    var lines = [];
    lines.push('고객: ' + q.client);
    if (q.contact) lines.push('연락처: ' + q.contact);
    lines.push('');
    lines.push('항목');
    q.items.forEach(function (item) {
      lines.push(
        '- ' + item.name + ' : ' + item.qty + ' x ' + calc.formatWon(item.price) +
        ' = ' + calc.formatWon(calc.lineTotal(item.qty, item.price))
      );
    });
    lines.push('');
    lines.push('합계: ' + calc.formatWon(calc.quoteTotal(q.items)));
    lines.push(calc.validUntilLabel(q.createdAt, q.validDays));
    return lines.join('\n');
  }

  // ---- 렌더링 ----
  function render() {
    approvedTotalEl.textContent = calc.formatWon(calc.approvedTotal(quotes));

    var sorted = quotes.slice().sort(function (a, b) {
      return new Date(b.updatedAt) - new Date(a.updatedAt);
    });

    emptyStateEl.hidden = sorted.length > 0;
    quoteListEl.innerHTML = '';

    sorted.forEach(function (q) {
      var tr = document.createElement('tr');

      var clientTd = document.createElement('td');
      clientTd.className = 'client-cell';
      var strong = document.createElement('strong');
      strong.textContent = q.client;
      var span = document.createElement('span');
      span.textContent = q.contact || '';
      clientTd.appendChild(strong);
      clientTd.appendChild(span);
      tr.appendChild(clientTd);

      var totalTd = document.createElement('td');
      totalTd.textContent = calc.formatWon(calc.quoteTotal(q.items));
      tr.appendChild(totalTd);

      var statusTd = document.createElement('td');
      var badge = document.createElement('span');
      badge.className = 'status-badge status-' + q.status;
      badge.textContent = statusLabel(q.status);
      statusTd.appendChild(badge);
      statusTd.appendChild(document.createElement('br'));

      var select = document.createElement('select');
      select.className = 'status-select';
      STATUSES.forEach(function (s) {
        var opt = document.createElement('option');
        opt.value = s.value;
        opt.textContent = s.label;
        if (s.value === q.status) opt.selected = true;
        select.appendChild(opt);
      });
      select.addEventListener('change', function () {
        handleStatusChange(q.id, select.value);
      });
      statusTd.appendChild(select);
      tr.appendChild(statusTd);

      var validTd = document.createElement('td');
      validTd.textContent = calc.validUntilLabel(q.createdAt, q.validDays);
      tr.appendChild(validTd);

      var actionsTd = document.createElement('td');
      actionsTd.className = 'actions-cell';
      actionsTd.appendChild(makeActionButton('수정', function () { openForm(q.id); }));
      actionsTd.appendChild(makeActionButton('복사', function () { copyQuote(q.id); }));
      actionsTd.appendChild(makeActionButton('인쇄', function () { printQuote(q.id); }));
      actionsTd.appendChild(makeActionButton('이력', function () { openHistory(q.id); }));
      actionsTd.appendChild(makeActionButton('삭제', function () { deleteQuote(q.id); }));
      tr.appendChild(actionsTd);

      quoteListEl.appendChild(tr);
    });
  }

  function makeActionButton(label, onClick) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn';
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  // ---- 상태 변경 (A-002, A-004) ----
  function handleStatusChange(id, newStatus) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q || newStatus === q.status) return;

    if (newStatus === 'sent') {
      previewContentEl.textContent = buildQuoteText(q);
      previewConfirmHandler = function () { applyStatusChange(id, newStatus); };
      previewDialog.showModal();
      render(); // 확정 전까지 select를 원래 상태로 되돌려 보여준다
      return;
    }
    applyStatusChange(id, newStatus);
  }

  function applyStatusChange(id, newStatus) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q) return;
    var oldLabel = statusLabel(q.status);
    q.status = newStatus;
    q.updatedAt = nowIso();
    q.history = q.history || [];
    q.history.push({ at: nowIso(), note: '상태 변경: ' + oldLabel + ' → ' + statusLabel(newStatus) });
    saveQuotes();
    render();
  }

  document.getElementById('previewConfirm').addEventListener('click', function () {
    if (previewConfirmHandler) previewConfirmHandler();
    previewConfirmHandler = null;
    previewDialog.close();
  });
  document.getElementById('previewCancel').addEventListener('click', function () {
    previewConfirmHandler = null;
    previewDialog.close();
  });
  previewDialog.addEventListener('close', render);

  // ---- 복사 / 인쇄 (A-005) ----
  function copyQuote(id) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q) return;
    var text = buildQuoteText(q);
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    var copied = false;
    try {
      copied = document.execCommand('copy');
    } catch (e) {
      copied = false;
    }
    document.body.removeChild(textarea);
    if (copied) {
      alert('견적 내용을 복사했어요. 이메일에 붙여넣으세요.');
    } else {
      alert('자동 복사에 실패했어요. 아래 내용을 직접 선택해 복사해주세요.\n\n' + text);
    }
  }

  function printQuote(id) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q) return;
    printAreaEl.textContent = buildQuoteText(q);
    window.print();
  }

  // ---- 수정 이력 (A-007) ----
  function openHistory(id) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q) return;
    historyListEl.innerHTML = '';
    var history = (q.history || []).slice().reverse();
    if (history.length === 0) {
      var li = document.createElement('li');
      li.textContent = '아직 수정 이력이 없어요.';
      historyListEl.appendChild(li);
    } else {
      history.forEach(function (h) {
        var item = document.createElement('li');
        var at = document.createElement('span');
        at.className = 'history-at';
        at.textContent = new Date(h.at).toLocaleString('ko-KR');
        item.appendChild(at);
        item.appendChild(document.createTextNode(h.note));
        historyListEl.appendChild(item);
      });
    }
    historyDialog.showModal();
  }
  document.getElementById('historyClose').addEventListener('click', function () {
    historyDialog.close();
  });

  // ---- 삭제 (A-010) ----
  function deleteQuote(id) {
    var q = quotes.filter(function (x) { return x.id === id; })[0];
    if (!q) return;
    var ok = confirm('"' + q.client + '" 견적을 삭제할까요? 되돌릴 수 없어요.');
    if (!ok) return;
    quotes = quotes.filter(function (x) { return x.id !== id; });
    saveQuotes();
    render();
  }

  // ---- 작성/수정 폼 (A-001, A-006, A-009) ----
  function addItemRow(item) {
    item = item || { name: '', qty: 1, price: 0 };
    var row = document.createElement('div');
    row.className = 'item-row';
    row.innerHTML =
      '<input type="text" class="item-name" placeholder="품목명 (예: 로고 디자인)">' +
      '<input type="number" class="item-qty" min="1" step="1" placeholder="수량">' +
      '<input type="number" class="item-price" min="0" step="100" placeholder="단가">' +
      '<span class="item-line-total">0원</span>' +
      '<button type="button" class="remove-item">삭제</button>';

    row.querySelector('.item-name').value = item.name;
    row.querySelector('.item-qty').value = item.qty;
    row.querySelector('.item-price').value = item.price;

    function updateLineTotal() {
      var qty = row.querySelector('.item-qty').value;
      var price = row.querySelector('.item-price').value;
      row.querySelector('.item-line-total').textContent = calc.formatWon(calc.lineTotal(qty, price));
      updateFormTotal();
    }
    row.querySelector('.item-qty').addEventListener('input', updateLineTotal);
    row.querySelector('.item-price').addEventListener('input', updateLineTotal);
    row.querySelector('.remove-item').addEventListener('click', function () {
      row.remove();
      updateFormTotal();
    });

    itemRowsEl.appendChild(row);
    updateLineTotal();
  }

  function updateFormTotal() {
    var items = readItemRows(false);
    formTotalEl.textContent = calc.formatWon(calc.quoteTotal(items));
  }

  function readItemRows(validate) {
    var rows = itemRowsEl.querySelectorAll('.item-row');
    var items = [];
    var error = null;
    rows.forEach(function (row) {
      var nameInput = row.querySelector('.item-name');
      var qtyInput = row.querySelector('.item-qty');
      var priceInput = row.querySelector('.item-price');
      nameInput.classList.remove('invalid');
      qtyInput.classList.remove('invalid');
      priceInput.classList.remove('invalid');

      var name = nameInput.value.trim();
      var qty = qtyInput.value;
      var price = priceInput.value;

      if (validate) {
        if (!name) {
          nameInput.classList.add('invalid');
          error = '품목명을 입력해주세요.';
        }
        var check = calc.validateLineItem(qty, price);
        if (!check.valid) {
          qtyInput.classList.add('invalid');
          priceInput.classList.add('invalid');
          error = check.error;
        }
      }
      items.push({ name: name, qty: Number(qty), price: Number(price) });
    });
    if (validate) {
      if (items.length === 0) error = '항목을 하나 이상 추가해주세요.';
      return { items: items, error: error };
    }
    return items;
  }

  function openForm(id) {
    editingId = id || null;
    itemRowsEl.innerHTML = '';
    formErrorEl.hidden = true;

    if (editingId) {
      var q = quotes.filter(function (x) { return x.id === editingId; })[0];
      document.getElementById('formTitle').textContent = '견적 수정';
      document.getElementById('clientInput').value = q.client;
      document.getElementById('contactInput').value = q.contact || '';
      document.getElementById('validDaysInput').value = q.validDays || 14;
      q.items.forEach(function (item) { addItemRow(item); });
    } else {
      document.getElementById('formTitle').textContent = '새 견적';
      document.getElementById('clientInput').value = '';
      document.getElementById('contactInput').value = '';
      document.getElementById('validDaysInput').value = 14;
      addItemRow();
    }
    updateFormTotal();
    formDialog.showModal();
  }

  document.getElementById('newQuoteBtn').addEventListener('click', function () { openForm(null); });
  document.getElementById('addItemRow').addEventListener('click', function () { addItemRow(); });
  document.getElementById('cancelForm').addEventListener('click', function () { formDialog.close(); });
  formDialog.addEventListener('close', render);

  quoteForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var client = document.getElementById('clientInput').value.trim();
    var contact = document.getElementById('contactInput').value.trim();
    var validDays = Number(document.getElementById('validDaysInput').value) || 0;

    var result = readItemRows(true);
    var items = result.items;
    var error = result.error;

    if (!client) {
      formErrorEl.textContent = '고객명을 입력해주세요.';
      formErrorEl.hidden = false;
      return;
    }
    if (error) {
      formErrorEl.textContent = error;
      formErrorEl.hidden = false;
      return;
    }
    formErrorEl.hidden = true;

    if (editingId) {
      var q = quotes.filter(function (x) { return x.id === editingId; })[0];
      var oldTotal = calc.quoteTotal(q.items);
      q.client = client;
      q.contact = contact;
      q.validDays = validDays;
      q.items = items;
      q.updatedAt = nowIso();
      var newTotal = calc.quoteTotal(items);
      q.history = q.history || [];
      q.history.push({
        at: nowIso(),
        note: oldTotal === newTotal
          ? '견적 내용 수정'
          : ('합계 수정: ' + calc.formatWon(oldTotal) + ' → ' + calc.formatWon(newTotal)),
      });
    } else {
      quotes.push({
        id: makeId(),
        client: client,
        contact: contact,
        items: items,
        validDays: validDays,
        status: 'draft',
        createdAt: nowIso(),
        updatedAt: nowIso(),
        history: [],
      });
    }

    saveQuotes();
    formDialog.close();
    render();
  });

  render();
})();
