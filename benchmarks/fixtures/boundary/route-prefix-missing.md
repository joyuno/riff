# Benchmark Fixture: 라우트 접두사 누락

## Fixture ID
`boundary-route-prefix`

## 평가 목표

Next.js App Router의 Route Group `(dashboard)` 구조에서 발생하는
경로 접두사 누락 버그들을 Riff가 탐지하는지 평가합니다.

---

## 프로젝트 구조

```
src/app/
├── (dashboard)/
│   ├── layout.tsx          ← 대시보드 공통 레이아웃
│   ├── orders/
│   │   └── page.tsx        ← 실제 경로: /orders
│   ├── products/
│   │   └── page.tsx        ← 실제 경로: /products
│   └── customers/
│       └── page.tsx        ← 실제 경로: /customers
├── (auth)/
│   ├── login/
│   │   └── page.tsx        ← 실제 경로: /login
│   └── register/
│       └── page.tsx        ← 실제 경로: /register
└── page.tsx                ← 실제 경로: /
```

_참고: `(dashboard)`는 Route Group이므로 URL 경로에 포함되지 않습니다._
_`src/app/(dashboard)/orders/page.tsx`의 실제 URL은 `/orders`입니다._

---

## 의도적 결함 코드

### 파일 1: `src/app/(dashboard)/orders/page.tsx`

```tsx
import Link from 'next/link';

export default function OrdersPage() {
  return (
    <div>
      <h1>주문 목록</h1>
      <nav>
        {/* DEFECT-1: Route Group 폴더명을 URL에 포함시킨 잘못된 링크 */}
        <Link href="/(dashboard)/products">상품 관리</Link>
        <Link href="/(dashboard)/customers">고객 관리</Link>

        {/* DEFECT-2: 올바른 링크 (참고용) */}
        {/* <Link href="/products">상품 관리</Link> */}
      </nav>
    </div>
  );
}
```

### 파일 2: `src/app/(dashboard)/layout.tsx`

```tsx
'use client';
import { useRouter } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  function handleLogout() {
    // 로그아웃 처리...
    // DEFECT-3: router.push에 존재하지 않는 경로 사용
    // /auth/login 경로는 없음. 올바른 경로는 /login
    router.push('/auth/login');
  }

  return (
    <div className="dashboard">
      <header>
        <button onClick={handleLogout}>로그아웃</button>
      </header>
      <main>{children}</main>
    </div>
  );
}
```

### 파일 3: `src/app/(dashboard)/customers/page.tsx`

```tsx
import { redirect } from 'next/navigation';

export default function CustomersPage() {
  // 어떤 조건에서...
  const isAdmin = false; // 예시

  if (!isAdmin) {
    // DEFECT-4: redirect 대상 경로도 잘못됨
    // /dashboard/orders 경로는 없음. 올바른 경로는 /orders
    redirect('/dashboard/orders');
  }

  return <div>고객 목록</div>;
}
```

### 파일 4: `src/middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // DEFECT-5: 보호 대상 경로 패턴이 실제 경로와 불일치
  // 실제 대시보드 경로는 /orders, /products, /customers 등
  // 여기서는 /dashboard/* 를 보호하려 하지만 해당 경로는 존재하지 않음
  const protectedPaths = ['/dashboard'];
  const isProtected = protectedPaths.some((p) => pathname.startsWith(p));

  if (isProtected) {
    const token = request.cookies.get('auth-token');
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

---

## 에이전트에게 제시될 메시지

```
다음 Next.js App Router 프로젝트에서 라우팅 관련 버그를 찾아주세요.

프로젝트 구조:
[위 구조 설명]

코드 파일:
[위 4개 파일]

Next.js Route Group (괄호 폴더)의 동작 방식과 실제 URL 경로의 관계에
집중하여 분석하세요.
```

---

## 심어진 결함 요약

| ID | 파일 | 결함 |
|----|------|------|
| DEFECT-1 | orders/page.tsx | `Link href`에 `(dashboard)` 그룹 접두사 포함 |
| DEFECT-2 | orders/page.tsx | 두 번째 Link도 동일 패턴 |
| DEFECT-3 | layout.tsx | `router.push('/auth/login')` — `/login`이어야 함 |
| DEFECT-4 | customers/page.tsx | `redirect('/dashboard/orders')` — `/orders`이어야 함 |
| DEFECT-5 | middleware.ts | matcher가 존재하지 않는 `/dashboard/*` 경로를 보호 |
