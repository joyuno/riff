# Benchmark Fixture: 반복 발생하는 Unwrap 버그

## Fixture ID
`immunity-unwrap`

## 평가 목표

한 번 수정된 버그 패턴이 다른 위치에서 반복 발생할 때,
Riff의 면역 시스템(항체 메커니즘)이 사전 방지하는지 평가합니다.

이 fixture는 **시간적 순서**가 있는 시나리오입니다.
Riff가 이전 수정 이력을 기억하고 동일 패턴의 재발을 막는지 측정합니다.

---

## 배경

이 프로젝트에서 "unwrap 버그"는 다음 패턴입니다:

```typescript
// API 라우트가 { data: [...] } 객체로 감싸서 반환
return NextResponse.json({ orders: result });

// 클라이언트 훅이 배열을 직접 기대
const { data } = useSWR<Order[]>(url, fetcher);
// → data.map(...)이 런타임에 실패 (data는 배열이 아니라 객체)
```

---

## 시나리오 타임라인

### Riff Turn 1~2: 초기 기능 구현

```
[T=1] User: 주문 API와 useOrders 훅 만들어줘
[T=2] Riff: /api/orders 라우트와 useOrders 훅 구현
```

구현 결과:
```typescript
// /api/orders/route.ts
return NextResponse.json({ orders: rows }); // 객체로 감쌈

// useOrders.ts
const { data } = useSWR<Order[]>('/api/orders', fetcher);
// data가 Order[]이길 기대하지만 실제로는 { orders: Order[] }
```

### Riff Turn 3: 버그 발견 및 수정

```
[T=3] User: useOrders에서 data.map is not a function 에러가 나요
[T=3] Riff: 수정 완료
  - /api/orders → return NextResponse.json(rows) 로 변경 (unwrap 제거)
  - 또는 useOrders → fetchJson<{ orders: Order[] }> 로 타입 수정
```

**항체 생성 시점**: Riff가 이 패턴을 학습해야 합니다.
"API가 객체로 감싸 반환하는 패턴 → 훅의 타입 기대와 불일치"

### Riff Turn 4~6: 상품 기능 추가

```
[T=4] User: 상품 목록 API도 만들어줘
[T=5] Riff: /api/products 라우트와 useProducts 훅 구현
[T=6] User: 상품 목록이 뜨네요. 이제 필터 기능 추가해줘
```

### Riff Turn 7: 동일 패턴 재발 (면역 시스템 테스트)

```
[T=7] 새로 구현된 /api/products/route.ts:
```

```typescript
// DEFECT: T=3에서 수정된 것과 동일한 unwrap 패턴 재발
export async function GET() {
  const products = await db.query('SELECT * FROM products');
  return NextResponse.json({ products: products.rows }); // ← 같은 패턴
}

// useProducts.ts
export function useProducts() {
  const { data } = useSWR<Product[]>('/api/products', fetcher);
  // data가 Product[]이길 기대하지만 { products: Product[] } 반환
  return { products: data ?? [] };
}
```

**평가 포인트**:
면역 시스템이 작동한다면 Riff는 T=7에서 코드를 작성하기 전에
"이 패턴은 T=3에서 이미 버그로 확인됨"을 언급하고 올바른 패턴으로 구현해야 합니다.

---

## 에이전트에게 제시될 메시지

```
다음은 이 프로젝트의 대화 히스토리입니다.

[Turn 1-2] 초기 주문 API와 훅 구현
[Turn 3] unwrap 버그 발견 및 수정 (상세 수정 내용 포함)
[Turn 4-6] 상품 기능 추가
[Turn 7] 새 /api/products 구현 요청

Turn 7에서 다음 코드를 구현하려고 합니다:

export async function GET() {
  const products = await db.query('SELECT * FROM products');
  return NextResponse.json({ products: products.rows });
}

export function useProducts() {
  const { data } = useSWR<Product[]>('/api/products', fetcher);
  return { products: data ?? [] };
}

이 구현에 대해 검토해주세요. 이전 대화 맥락을 고려하세요.
```

---

## 면역 시스템 체크포인트

| 체크포인트 | 설명 | 가중치 |
|-----------|------|--------|
| **항체 생성** | T=3 수정 시 "이 패턴은 다른 곳에도 적용해야 함"을 언급 | CRITICAL |
| **재발 감지** | T=7 코드 검토 시 T=3과 동일 패턴임을 인식 | CRITICAL |
| **사전 방지** | T=7에서 버그 패턴 사용 전에 경고 또는 올바른 패턴으로 수정 | MAJOR |

좋은 면역 시스템 점수: 3개 모두 감지
최소 합격: 재발 감지 + 사전 방지
