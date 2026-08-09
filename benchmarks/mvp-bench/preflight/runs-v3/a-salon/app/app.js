// A-007: 손님 정보는 이 브라우저의 localStorage에만 저장한다. 외부로 전송하는 코드는 없다.
const STORAGE_KEY = 'salon_reservations_v1';
const STATUSES = ['예약중', '완료', '취소', '노쇼'];
const BLOCKING_STATUSES = ['예약중', '완료']; // A-005: 슬롯을 점유 중인 것으로 보는 상태

function loadReservations() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveReservations(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

function toMinutes(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

// A-005: 같은 날짜에 소요시간이 겹치는 예약(예약중/완료)이 있으면 true
function hasOverlap(list, { date, time, duration }, excludeId) {
  const startA = toMinutes(time);
  const endA = startA + Number(duration);
  return list.some((r) => {
    if (r.id === excludeId) return false;
    if (r.date !== date) return false;
    if (!BLOCKING_STATUSES.includes(r.status)) return false;
    const startB = toMinutes(r.time);
    const endB = startB + Number(r.duration);
    return startA < endB && startB < endA;
  });
}

// A-006: 같은 전화번호의 과거 노쇼 횟수
function noShowCount(list, phone) {
  if (!phone) return 0;
  return list.filter((r) => r.phone === phone && r.status === '노쇼').length;
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

function init() {
  let reservations = loadReservations();

  const form = document.getElementById('reservation-form');
  const errorEl = document.getElementById('form-error');
  const phoneInput = document.getElementById('f-phone');
  const noshowHint = document.getElementById('noshow-hint');
  const filterDate = document.getElementById('filter-date');
  const filterSearch = document.getElementById('filter-search');
  const tbody = document.getElementById('reservation-body');
  const emptyMsg = document.getElementById('empty-msg');
  const summaryTotal = document.getElementById('summary-total');
  const summaryByService = document.getElementById('summary-by-service');

  filterDate.value = todayStr();
  document.getElementById('f-date').value = todayStr();

  phoneInput.addEventListener('input', () => {
    const n = noShowCount(reservations, phoneInput.value.trim());
    noshowHint.textContent = n > 0 ? `이 손님 과거 노쇼 ${n}회` : '';
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    errorEl.textContent = '';

    const entry = {
      id: Date.now() + '-' + Math.random().toString(36).slice(2, 7),
      name: document.getElementById('f-name').value.trim(),
      phone: phoneInput.value.trim(),
      service: document.getElementById('f-service').value.trim(),
      date: document.getElementById('f-date').value,
      time: document.getElementById('f-time').value,
      duration: document.getElementById('f-duration').value,
      price: document.getElementById('f-price').value,
      status: '예약중',
    };

    if (hasOverlap(reservations, entry, null)) {
      errorEl.textContent = '이미 그 시간대에 예약이 있어요. 다른 시간을 선택해주세요.';
      return;
    }

    reservations.push(entry);
    saveReservations(reservations);
    form.reset();
    document.getElementById('f-date').value = filterDate.value || todayStr();
    document.getElementById('f-duration').value = 60;
    noshowHint.textContent = '';
    render();
  });

  filterDate.addEventListener('change', render);
  filterSearch.addEventListener('input', render);

  function changeStatus(id, newStatus) {
    const r = reservations.find((x) => x.id === id);
    if (!r) return;
    r.status = newStatus;
    saveReservations(reservations);
    render();
  }

  function visibleReservations() {
    const q = filterSearch.value.trim().toLowerCase();
    if (q) {
      // A-008: 검색어가 있으면 날짜 무관 전체에서 찾는다
      return reservations.filter((r) =>
        r.name.toLowerCase().includes(q) ||
        r.phone.toLowerCase().includes(q) ||
        r.service.toLowerCase().includes(q)
      );
    }
    return reservations.filter((r) => r.date === filterDate.value);
  }

  function render() {
    const list = visibleReservations().slice().sort((a, b) => a.time.localeCompare(b.time));
    tbody.innerHTML = '';
    emptyMsg.hidden = list.length > 0;

    for (const r of list) {
      const tr = document.createElement('tr');
      const nShow = noShowCount(reservations, r.phone);
      tr.innerHTML = `
        <td>${r.time}</td>
        <td>${r.name}</td>
        <td>${r.phone}</td>
        <td>${r.service}</td>
        <td>${r.duration}분</td>
        <td>${Number(r.price).toLocaleString()}원</td>
        <td><span class="badge status-${r.status}">${r.status}</span></td>
        <td>${nShow > 0 ? `<span class="noshow-count">${nShow}회</span>` : '-'}</td>
        <td class="actions"></td>
      `;
      const actionsCell = tr.querySelector('.actions');
      for (const s of STATUSES) {
        if (s === r.status) continue;
        const btn = document.createElement('button');
        btn.textContent = s;
        btn.addEventListener('click', () => changeStatus(r.id, s));
        actionsCell.appendChild(btn);
      }
      tbody.appendChild(tr);
    }

    // A-003: 선택한 날짜의 완료 예약 매출 요약
    const completedToday = reservations.filter(
      (r) => r.date === filterDate.value && r.status === '완료'
    );
    const total = completedToday.reduce((sum, r) => sum + Number(r.price), 0);
    summaryTotal.textContent = `총 ${total.toLocaleString()}원 (${completedToday.length}건)`;

    const byService = {};
    for (const r of completedToday) {
      byService[r.service] = (byService[r.service] || 0) + Number(r.price);
    }
    summaryByService.innerHTML = Object.entries(byService)
      .map(([svc, amt]) => `<li>${svc}: ${amt.toLocaleString()}원</li>`)
      .join('');
  }

  render();
}

document.addEventListener('DOMContentLoaded', init);
