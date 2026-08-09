// ---- 순수 로직 (Node에서도 require해서 테스트 가능) ----

const VAT_RATE = 0.1;

function calcAmounts(rawAmount, vatMode) {
  const amt = Math.round(rawAmount);
  if (vatMode === 'inclusive') {
    const supply = Math.round(amt / (1 + VAT_RATE));
    const vat = amt - supply;
    return { supply, vat, total: amt };
  }
  const vat = Math.round(amt * VAT_RATE);
  return { supply: amt, vat, total: amt + vat };
}

function isValidAmount(v) {
  return typeof v === 'number' && Number.isFinite(v) && v > 0;
}

function sumApproved(quotes) {
  return quotes
    .filter((q) => q.status === 'approved' && !q.archived)
    .reduce((sum, q) => sum + q.total, 0);
}

function formatCurrency(n) {
  return `${Math.round(n).toLocaleString('ko-KR')}원`;
}

const STATUS_LABEL = { draft: '초안', sent: '발송', approved: '승인', rejected: '거절' };

if (typeof module !== 'undefined') {
  module.exports = { calcAmounts, isValidAmount, sumApproved, formatCurrency };
}

// ---- 브라우저 UI (document 없으면 Node 테스트 환경이므로 건너뜀) ----

if (typeof document !== 'undefined') {
  const STORAGE_KEY = 'cquotes.v1';

  const state = { showArchived: false };

  function loadQuotes() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveQuotes(quotes) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(quotes));
  }

  let quotes = loadQuotes();

  const form = document.getElementById('quoteForm');
  const clientInput = document.getElementById('client');
  const itemDescInput = document.getElementById('itemDesc');
  const amountInput = document.getElementById('amount');
  const vatModeInput = document.getElementById('vatMode');
  const scopeInput = document.getElementById('scope');
  const formError = document.getElementById('formError');

  const searchInput = document.getElementById('searchClient');
  const statusFilter = document.getElementById('statusFilter');
  const toggleArchiveBtn = document.getElementById('toggleArchive');
  const quoteList = document.getElementById('quoteList');
  const emptyMsg = document.getElementById('emptyMsg');
  const approvedSumEl = document.getElementById('approvedSum');
  const rowTemplate = document.getElementById('quoteRowTemplate');

  function showError(msg) {
    formError.textContent = msg;
    formError.hidden = false;
  }

  function clearError() {
    formError.hidden = true;
    formError.textContent = '';
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    clearError();

    const client = clientInput.value.trim();
    const amount = Number(amountInput.value);

    if (!client) {
      showError('고객명을 입력해주세요.');
      return;
    }
    if (!isValidAmount(amount)) {
      showError('금액은 0보다 큰 숫자로 입력해주세요.');
      return;
    }

    const { supply, vat, total } = calcAmounts(amount, vatModeInput.value);
    quotes.push({
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      client,
      itemDesc: itemDescInput.value.trim(),
      scope: scopeInput.value.trim(),
      vatMode: vatModeInput.value,
      supply,
      vat,
      total,
      status: 'draft',
      archived: false,
      createdAt: new Date().toISOString(),
    });
    saveQuotes(quotes);
    form.reset();
    vatModeInput.value = 'exclusive';
    render();
  });

  searchInput.addEventListener('input', render);
  statusFilter.addEventListener('change', render);
  toggleArchiveBtn.addEventListener('click', () => {
    state.showArchived = !state.showArchived;
    toggleArchiveBtn.textContent = state.showArchived ? '진행 중 목록 보기' : '보관함 보기';
    render();
  });

  quoteList.addEventListener('change', (e) => {
    if (!e.target.classList.contains('statusSelect')) return;
    const id = e.target.closest('.quote-card').dataset.id;
    const q = quotes.find((x) => x.id === id);
    if (!q) return;
    q.status = e.target.value;
    saveQuotes(quotes);
    render();
  });

  quoteList.addEventListener('click', (e) => {
    const card = e.target.closest('.quote-card');
    if (!card) return;
    const id = card.dataset.id;
    const q = quotes.find((x) => x.id === id);
    if (!q) return;

    if (e.target.classList.contains('archiveBtn')) {
      q.archived = true;
      saveQuotes(quotes);
      render();
    } else if (e.target.classList.contains('restoreBtn')) {
      q.archived = false;
      saveQuotes(quotes);
      render();
    }
  });

  function getFiltered() {
    const term = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;
    return quotes.filter((q) => {
      if (!!q.archived !== state.showArchived) return false;
      if (term && !q.client.toLowerCase().includes(term)) return false;
      if (status !== 'all' && q.status !== status) return false;
      return true;
    });
  }

  function render() {
    const filtered = getFiltered().slice().sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    quoteList.innerHTML = '';
    emptyMsg.hidden = filtered.length > 0;

    filtered.forEach((q) => {
      const node = rowTemplate.content.cloneNode(true);
      const card = node.querySelector('.quote-card');
      card.dataset.id = q.id;
      card.classList.add(`status-${q.status}`);
      if (q.archived) card.classList.add('archived');

      node.querySelector('.quote-client').textContent = q.client;
      node.querySelector('.quote-item').textContent = q.itemDesc || '(항목 설명 없음)';
      node.querySelector('.quote-scope').textContent = q.scope ? `수정 범위: ${q.scope}` : '';
      node.querySelector('.quote-supply').textContent = `공급가 ${formatCurrency(q.supply)}`;
      node.querySelector('.quote-vat').textContent = `부가세 ${formatCurrency(q.vat)}`;
      node.querySelector('.quote-total').textContent = `합계 ${formatCurrency(q.total)}`;

      const select = node.querySelector('.statusSelect');
      select.value = q.status;

      quoteList.appendChild(node);
    });

    approvedSumEl.textContent = formatCurrency(sumApproved(quotes));
  }

  render();
}
