# Benchmark Fixture: API↔훅 Shape 불일치

## Fixture ID
`boundary-api-shape`

## 평가 목표

API 라우트와 클라이언트 훅 사이의 경계면에 심어진 shape 불일치 버그들을
Riff가 얼마나 잘 탐지하는지 평가합니다.

---

## 의도적 결함 코드

### 파일 1: `src/app/api/orders/route.ts` (API 라우트)

```typescript
import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('userId');

  const orders = await db.query(
    `SELECT order_id, user_id, created_at, total_amount, order_status
     FROM orders WHERE user_id = $1`,
    [userId]
  );

  // DEFECT-1: 배열을 { orders: [...] } 객체로 감싸서 반환
  // 클라이언트 훅은 배열을 직접 기대함
  return NextResponse.json({ orders: orders.rows });
}

export async function PATCH(request: Request) {
  const body = await request.json();
  const { orderId, status } = body;

  // DEFECT-3: 상태 전이 검증 없음
  // 'delivered' → 'pending' 같은 역방향 전이 허용
  await db.query(
    `UPDATE orders SET order_status = $1 WHERE order_id = $2`,
    [status, orderId]
  );

  return NextResponse.json({ success: true });
}
```

### 파일 2: `src/hooks/useOrders.ts` (클라이언트 훅)

```typescript
import useSWR from 'swr';
import { fetchJson } from '@/lib/fetcher';

interface Order {
  orderId: string;      // camelCase
  userId: string;       // camelCase
  createdAt: string;    // camelCase
  totalAmount: number;  // camelCase
  orderStatus: string;  // camelCase
}

export function useOrders(userId: string) {
  // DEFECT-1 연동: 배열을 직접 기대하지만 API는 { orders: [...] } 반환
  const { data, error } = useSWR<Order[]>(
    `/api/orders?userId=${userId}`,
    fetchJson
  );

  // DEFECT-2: DB는 snake_case (order_id, created_at) 반환
  // 훅은 camelCase (orderId, createdAt) 기대
  // 변환 레이어 없음 → 모든 필드가 undefined
  return {
    orders: data ?? [],
    isLoading: !error && !data,
    error,
  };
}
```

### 파일 3: `src/lib/fetcher.ts` (fetcher 유틸)

```typescript
export async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  // DEFECT-4: 에러 응답의 body를 읽지 않음
  // 서버가 { error: "Not found" } 반환해도 메시지 소실
  return res.json();
}
```

### 파일 4: `src/components/OrderStatusBadge.tsx` (UI 컴포넌트)

```typescript
const STATUS_LABELS: Record<string, string> = {
  pending: '대기중',
  processing: '처리중',
  shipped: '배송중',
  delivered: '배송완료',
};

export function OrderStatusBadge({ status }: { status: string }) {
  // DEFECT-5: DB에서 오는 'order_status' 값이 snake_case면
  // 예: 'in_progress' → STATUS_LABELS에 없음 → undefined → 렌더링 깨짐
  return (
    <span className={`badge badge-${status}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
```

---

## 에이전트에게 제시될 메시지

```
다음 Next.js 코드에서 API 라우트와 클라이언트 훅 사이의 경계면 버그를 찾아주세요.

[위 4개 파일의 코드를 그대로 붙여넣기]

특히 데이터 shape 불일치, 필드명 변환 누락, 상태 전이 오류를 중심으로 분석하세요.
```

---

## 심어진 결함 요약

| ID | 파일 | 결함 |
|----|------|------|
| DEFECT-1 | route.ts + useOrders.ts | API는 `{orders:[]}` 반환, 훅은 `Order[]` 기대 |
| DEFECT-2 | DB→훅 | snake_case → camelCase 변환 레이어 없음 |
| DEFECT-3 | route.ts PATCH | 상태 전이 검증 없음 (역방향 허용) |
| DEFECT-4 | fetcher.ts | 에러 응답 body 미파싱 |
| DEFECT-5 | OrderStatusBadge | DB 값과 STATUS_LABELS 키 불일치 가능성 |
