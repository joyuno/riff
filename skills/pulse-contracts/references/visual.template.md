# Visual Contract: {모듈명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: {에이전트명}
> 상태: draft | active | deprecated

---

## 개요

{이 계약서가 다루는 UI 컴포넌트 또는 페이지 설명}

---

## 컴포넌트 상태 정의

### {컴포넌트명} (예: PrimaryButton)

| 상태 | 시각적 표현 | 인터랙션 | 접근성 |
|------|------------|---------|--------|
| `default` | 배경: `--color-primary-500` | 클릭 가능 | `aria-disabled="false"` |
| `hover` | 배경: `--color-primary-600` | 커서: pointer | — |
| `active` | 배경: `--color-primary-700`, scale: 0.98 | — | — |
| `disabled` | 배경: `--color-neutral-300`, 텍스트: `--color-neutral-500` | 클릭 불가 | `aria-disabled="true"`, `tabindex="-1"` |
| `loading` | 배경: `--color-primary-500`, 스피너 표시 | 클릭 불가 | `aria-busy="true"` |
| `success` | 배경: `--color-success-500`, 체크 아이콘 | — | `aria-label="완료"` |
| `error` | 배경: `--color-error-500` | 클릭 가능 (재시도) | `aria-label="오류 발생, 재시도"` |

### {컴포넌트명} (예: InputField)

| 상태 | 테두리 | 배경 | 레이블 |
|------|--------|------|--------|
| `default` | `--color-neutral-300` | `--color-white` | `--color-neutral-700` |
| `focus` | `--color-primary-500`, 2px | `--color-white` | `--color-primary-600` |
| `filled` | `--color-neutral-400` | `--color-white` | `--color-neutral-700` |
| `error` | `--color-error-500` | `--color-error-50` | `--color-error-600` |
| `disabled` | `--color-neutral-200` | `--color-neutral-100` | `--color-neutral-400` |
| `readonly` | `--color-neutral-200` | `--color-neutral-50` | `--color-neutral-600` |

---

## 반응형 브레이크포인트

| 이름 | 최소 너비 | 레이아웃 변경 |
|------|----------|--------------|
| `mobile` | 0px | 1컬럼, 풀너비 |
| `tablet` | 768px | 2컬럼, 사이드바 숨김 |
| `desktop` | 1024px | 3컬럼, 사이드바 표시 |
| `wide` | 1440px | 콘텐츠 최대 너비 1280px |

### 컴포넌트별 반응형 규칙

| 컴포넌트 | mobile | tablet | desktop |
|---------|--------|--------|---------|
| `PageHeader` | 제목만 표시 | 제목 + 액션 버튼 | 제목 + 액션 버튼 + 서브텍스트 |
| `DataTable` | 카드 뷰 전환 | 핵심 컬럼 3개만 | 전체 컬럼 |
| `Sidebar` | 숨김 (드로어) | 아이콘만 | 전체 텍스트 |

---

## 디자인 토큰

### 색상

```
/* 주요 색상 */
--color-primary-50: #eff6ff;
--color-primary-500: #3b82f6;
--color-primary-600: #2563eb;
--color-primary-700: #1d4ed8;

/* 의미론적 색상 */
--color-success-500: #22c55e;
--color-error-500: #ef4444;
--color-warning-500: #f59e0b;

/* 중립 색상 */
--color-neutral-50: #f9fafb;
--color-neutral-100: #f3f4f6;
--color-neutral-200: #e5e7eb;
--color-neutral-300: #d1d5db;
--color-neutral-400: #9ca3af;
--color-neutral-500: #6b7280;
--color-neutral-700: #374151;
--color-white: #ffffff;
```

### 타이포그래피

```
/* 폰트 패밀리 */
--font-sans: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* 폰트 크기 */
--text-xs: 0.75rem;   /* 12px */
--text-sm: 0.875rem;  /* 14px */
--text-base: 1rem;    /* 16px */
--text-lg: 1.125rem;  /* 18px */
--text-xl: 1.25rem;   /* 20px */
--text-2xl: 1.5rem;   /* 24px */
--text-3xl: 1.875rem; /* 30px */

/* 폰트 굵기 */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* 행간 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### 간격

```
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### 그림자

```
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
```

### 모서리 반경

```
--radius-sm: 0.25rem;  /* 4px */
--radius-md: 0.375rem; /* 6px */
--radius-lg: 0.5rem;   /* 8px */
--radius-xl: 0.75rem;  /* 12px */
--radius-full: 9999px;
```

---

## 애니메이션

| 용도 | Duration | Easing | 비고 |
|------|----------|--------|------|
| 버튼 hover | 150ms | ease-out | 색상 전환 |
| 모달 열림 | 200ms | ease-out | scale(0.95) → scale(1) |
| 모달 닫힘 | 150ms | ease-in | scale(1) → scale(0.95) |
| 토스트 등장 | 300ms | spring | translateY(-100%) → 0 |
| 페이지 전환 | 250ms | ease-in-out | opacity 0 → 1 |
| 스켈레톤 | 1500ms | linear, 반복 | shimmer 효과 |

---

## 접근성 요구사항

- 색상 대비: WCAG AA 기준 (일반 텍스트 4.5:1, 대형 텍스트 3:1)
- 포커스 링: 모든 인터랙티브 요소에 `outline: 2px solid --color-primary-500`
- 스크린 리더: 모든 아이콘 버튼에 `aria-label` 필수
- 키보드 내비게이션: Tab 순서는 시각적 순서와 일치

---

## 변경 이력

| 날짜 | 변경 내용 | 변경자 |
|------|-----------|--------|
| {YYYY-MM-DD} | 최초 생성 | {에이전트명} |
