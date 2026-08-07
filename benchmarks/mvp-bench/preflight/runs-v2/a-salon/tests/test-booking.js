// PROVE Tier 2 실행 가능 체크 — booking.js 핵심 로직(A-002, A-003, A-006) 검증
// 실행: node tests/test-booking.js
const assert = require('assert');
const api = require('../app/js/booking.js');

// A-002: 겹치는 예약은 저장 거부(활성 상태만)
{
  const existing = [{ id: '1', date: '2026-08-10', startTime: '14:00', durationMin: 60, status: 'scheduled', customerName: '김손님' }];
  const overlapping = { date: '2026-08-10', startTime: '14:30', durationMin: 30 };
  const conflict = api.findOverlap(existing, overlapping);
  assert.ok(conflict && conflict.id === '1', '겹치는 시간대는 충돌로 감지되어야 한다');

  const nonOverlapping = { date: '2026-08-10', startTime: '15:00', durationMin: 30 };
  assert.strictEqual(api.findOverlap(existing, nonOverlapping), null, '겹치지 않는 시간대는 충돌이 아니어야 한다');

  const differentDate = { date: '2026-08-11', startTime: '14:00', durationMin: 30 };
  assert.strictEqual(api.findOverlap(existing, differentDate), null, '다른 날짜는 충돌이 아니어야 한다');
}

// A-002 예외: 취소·노쇼 상태는 시간대 재사용 허용
{
  const cancelled = [{ id: '2', date: '2026-08-10', startTime: '14:00', durationMin: 60, status: 'cancelled' }];
  const candidate = { date: '2026-08-10', startTime: '14:00', durationMin: 60 };
  assert.strictEqual(api.findOverlap(cancelled, candidate), null, '취소된 예약과는 겹쳐도 저장 가능해야 한다');
}

// A-003: 손님별 노쇼 누적 횟수
{
  const list = [
    { phone: '010-1111-2222', status: 'noshow' },
    { phone: '010-1111-2222', status: 'noshow' },
    { phone: '010-1111-2222', status: 'completed' },
    { phone: '010-3333-4444', status: 'noshow' },
  ];
  assert.strictEqual(api.countNoShows(list, '010-1111-2222'), 2, '노쇼 2회가 정확히 집계되어야 한다');
  assert.strictEqual(api.countNoShows(list, '010-9999-0000'), 0, '기록 없는 손님은 0이어야 한다');
}

// A-006: 완료 상태 예약만 매출에 합산
{
  const list = [
    { date: '2026-08-10', status: 'completed', price: 50000 },
    { date: '2026-08-10', status: 'scheduled', price: 40000 },
    { date: '2026-08-10', status: 'completed', price: 30000 },
    { date: '2026-08-11', status: 'completed', price: 99999 },
  ];
  assert.strictEqual(api.sumRevenue(list, '2026-08-10'), 80000, '완료 상태 예약 금액만 합산되어야 한다');
}

// A-004: 날짜별 필터 + 시간순 정렬 (내일 예약 보기의 기반 로직)
{
  const list = [
    { date: '2026-08-11', startTime: '15:00' },
    { date: '2026-08-11', startTime: '09:00' },
    { date: '2026-08-10', startTime: '10:00' },
  ];
  const tomorrow = api.filterByDate(list, '2026-08-11');
  assert.strictEqual(tomorrow.length, 2);
  assert.strictEqual(tomorrow[0].startTime, '09:00', '시간순으로 정렬되어야 한다');
}

// localStorage 저장/로드 왕복 (간단한 in-memory mock)
{
  const store = {};
  const mockStorage = {
    getItem: (k) => store[k] || null,
    setItem: (k, v) => { store[k] = v; },
  };
  const data = [{ id: 'x', date: '2026-08-10' }];
  api.saveReservations(mockStorage, data);
  const loaded = api.loadReservations(mockStorage);
  assert.deepStrictEqual(loaded, data, '저장한 값을 그대로 다시 읽을 수 있어야 한다');
}

console.log('OK: booking.js 전체 체크 통과 (A-002, A-003, A-004, A-006)');
