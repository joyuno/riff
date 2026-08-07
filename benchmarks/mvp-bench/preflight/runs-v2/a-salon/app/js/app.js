// app.js — 화면 렌더링과 이벤트 처리 (booking.js의 순수 로직을 사용)
(function () {
  const api = window.bookingApi;
  let reservations = api.loadReservations(window.localStorage);

  const dateInput = document.getElementById('date-input');
  const todayBtn = document.getElementById('today-btn');
  const tomorrowBtn = document.getElementById('tomorrow-btn');
  const revenueEl = document.getElementById('revenue-summary');
  const listEl = document.getElementById('reservation-list');
  const form = document.getElementById('add-form');
  const errorEl = document.getElementById('form-error');

  function todayStr(offsetDays = 0) {
    const d = new Date();
    d.setDate(d.getDate() + offsetDays);
    return d.toISOString().slice(0, 10);
  }

  function persist() {
    api.saveReservations(window.localStorage, reservations);
  }

  const STATUS_LABEL = {
    scheduled: '예정',
    completed: '완료',
    noshow: '노쇼',
    cancelled: '취소',
  };

  function render() {
    const date = dateInput.value || todayStr();
    const dayList = api.filterByDate(reservations, date);

    revenueEl.textContent = `오늘 매출(완료 기준): ${api.sumRevenue(reservations, date).toLocaleString()}원`;

    if (dayList.length === 0) {
      listEl.innerHTML = '<p class="empty">이 날짜에 예약이 없습니다.</p>';
      return;
    }

    listEl.innerHTML = dayList
      .map((r) => {
        const noshowCount = api.countNoShows(reservations, r.phone);
        const endMin = api.getRange(r).end;
        const endTime = `${String(Math.floor(endMin / 60)).padStart(2, '0')}:${String(endMin % 60).padStart(2, '0')}`;
        return `
        <div class="reservation-card status-${r.status}" data-id="${r.id}">
          <div class="rc-time">${r.startTime}~${endTime}</div>
          <div class="rc-main">
            <div class="rc-name">${escapeHtml(r.customerName)} ${r.phone ? `<span class="rc-phone">${escapeHtml(r.phone)}</span>` : ''}
              ${noshowCount > 0 ? `<span class="badge badge-warn">노쇼 ${noshowCount}회</span>` : ''}</div>
            <div class="rc-service">${escapeHtml(r.service)}${r.price ? ` · ${Number(r.price).toLocaleString()}원` : ''}</div>
            ${r.memo ? `<div class="rc-memo">${escapeHtml(r.memo)}</div>` : ''}
          </div>
          <div class="rc-status badge badge-${r.status}">${STATUS_LABEL[r.status]}</div>
          <div class="rc-actions">
            ${r.status !== 'completed' ? `<button data-action="completed">완료</button>` : ''}
            ${r.status !== 'noshow' ? `<button data-action="noshow">노쇼</button>` : ''}
            ${r.status !== 'cancelled' ? `<button data-action="cancelled">취소</button>` : ''}
            ${r.status !== 'scheduled' ? `<button data-action="scheduled">예정으로</button>` : ''}
            <button data-action="delete" class="danger">삭제</button>
          </div>
        </div>`;
      })
      .join('');
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  listEl.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const card = e.target.closest('.reservation-card');
    const id = card.dataset.id;
    const action = btn.dataset.action;

    if (action === 'delete') {
      if (!window.confirm('정말 삭제하시겠습니까? 되돌릴 수 없습니다.')) return; // A-005
      reservations = reservations.filter((r) => r.id !== id);
    } else {
      reservations = reservations.map((r) => (r.id === id ? { ...r, status: action } : r));
    }
    persist();
    render();
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    errorEl.textContent = '';

    const candidate = {
      id: Date.now().toString(),
      customerName: form.customerName.value.trim(),
      phone: form.phone.value.trim(),
      date: form.date.value,
      startTime: form.startTime.value,
      service: form.service.value.trim(),
      durationMin: Number(form.durationMin.value),
      price: form.price.value ? Number(form.price.value) : 0,
      memo: form.memo.value.trim(),
      status: 'scheduled',
    };

    if (!candidate.customerName || !candidate.date || !candidate.startTime || !candidate.service || !candidate.durationMin) {
      errorEl.textContent = '고객명·날짜·시작 시각·시술명·소요 시간은 필수입니다.';
      return;
    }

    const conflict = api.findOverlap(reservations, candidate); // A-002
    if (conflict) {
      errorEl.textContent = `${conflict.startTime} ${conflict.customerName}님 예약과 겹칩니다. 시간을 바꿔주세요.`;
      return;
    }

    reservations.push(candidate);
    persist();
    form.reset();
    dateInput.value = candidate.date;
    render();
  });

  dateInput.addEventListener('change', render);
  todayBtn.addEventListener('click', () => {
    dateInput.value = todayStr();
    render();
  });
  tomorrowBtn.addEventListener('click', () => {
    dateInput.value = todayStr(1); // A-004: 내일 예약 보기
    render();
  });

  dateInput.value = todayStr();
  form.date.value = todayStr();
  render();
})();
