// booking.js — 예약 데이터 순수 로직 (DOM 없음, 브라우저/Node 양쪽에서 로드 가능)
// A-001, A-002, A-003, A-004, A-006 근거 로직

const STORAGE_KEY = 'salon_reservations_v1';

// 겹침 판정에서 "막혀 있는" 것으로 취급할 상태 (A-002: 취소·노쇼는 시간대 재사용 허용)
const ACTIVE_STATUSES = ['scheduled', 'completed'];

function timeToMinutes(hhmm) {
  const [h, m] = String(hhmm).split(':').map(Number);
  return h * 60 + m;
}

// 예약의 [시작, 종료) 구간(분 단위)
function getRange(res) {
  const start = timeToMinutes(res.startTime);
  return { start, end: start + Number(res.durationMin) };
}

// 같은 날짜에서 겹치는 활성 예약을 찾는다. candidateId는 수정 시 자기 자신 제외용(현재 MVP는 미사용, 확장 대비).
function findOverlap(reservations, candidate, candidateId) {
  const range = getRange(candidate);
  for (const res of reservations) {
    if (res.id === candidateId) continue;
    if (res.date !== candidate.date) continue;
    if (!ACTIVE_STATUSES.includes(res.status)) continue;
    const other = getRange(res);
    if (range.start < other.end && other.start < range.end) {
      return res;
    }
  }
  return null;
}

function filterByDate(reservations, date) {
  return reservations
    .filter((r) => r.date === date)
    .sort((a, b) => timeToMinutes(a.startTime) - timeToMinutes(b.startTime));
}

// 전화번호 기준 노쇼 누적 횟수 (A-003). 전화번호 없으면 0.
function countNoShows(reservations, phone) {
  if (!phone) return 0;
  return reservations.filter((r) => r.phone === phone && r.status === 'noshow').length;
}

// 완료된 예약 금액 합 (A-006)
function sumRevenue(reservations, date) {
  return filterByDate(reservations, date)
    .filter((r) => r.status === 'completed')
    .reduce((sum, r) => sum + (Number(r.price) || 0), 0);
}

function loadReservations(storage) {
  const raw = storage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveReservations(storage, list) {
  storage.setItem(STORAGE_KEY, JSON.stringify(list));
}

const bookingApi = {
  STORAGE_KEY,
  timeToMinutes,
  getRange,
  findOverlap,
  filterByDate,
  countNoShows,
  sumRevenue,
  loadReservations,
  saveReservations,
};

// 브라우저(<script>)와 Node(require) 양쪽에서 쓸 수 있게 가드
if (typeof module !== 'undefined' && module.exports) {
  module.exports = bookingApi;
} else {
  window.bookingApi = bookingApi;
}
