# Type Contract: {모듈명}

> 생성일: {YYYY-MM-DD}
> 생성자: {에이전트명}
> 소비자: {에이전트명}
> 상태: draft | active | deprecated

---

## API Endpoints

| Method | Path | Request Body | Response Body | Status Codes |
|--------|------|-------------|---------------|-------------|
| POST | /api/example | `{ name: string }` | `{ id: string, name: string }` | 201, 400, 500 |
| GET | /api/example/:id | — | `{ id: string, name: string }` | 200, 404, 500 |
| PUT | /api/example/:id | `{ name?: string }` | `{ id: string, name: string }` | 200, 400, 404, 500 |
| DELETE | /api/example/:id | — | — | 204, 404, 500 |

---

## Shared Types

```typescript
// 공유 타입 정의 (프론트엔드와 백엔드가 모두 참조)

interface Example {
  id: string;           // UUID
  name: string;         // 1-100자
  createdAt: string;    // ISO 8601
  updatedAt: string;    // ISO 8601
}

interface CreateExampleRequest {
  name: string;
}

interface ExampleResponse {
  data: Example;
}

interface ExampleListResponse {
  data: Example[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
  };
}

interface ErrorResponse {
  error: {
    code: string;       // 'VALIDATION_ERROR', 'NOT_FOUND', 'UNAUTHORIZED'
    message: string;
    details?: Record<string, string[]>;  // 필드별 에러 목록
  };
}
```

---

## 에러 코드 목록

| HTTP Status | Error Code | 의미 |
|-------------|-----------|------|
| 400 | `VALIDATION_ERROR` | 요청 데이터 유효성 검사 실패 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 또는 만료 |
| 403 | `FORBIDDEN` | 권한 없음 |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 409 | `CONFLICT` | 중복 리소스 |
| 500 | `INTERNAL_ERROR` | 서버 내부 오류 |

---

## 주의사항

### 래핑 규칙
- 단일 리소스: `{ data: {...} }` 형태로 래핑
- 목록: `{ data: [...], pagination: {...} }` 형태로 래핑
- 삭제 성공: body 없음 (204 No Content)
- 에러: `{ error: {...} }` 형태로 래핑

### 네이밍 컨벤션
- 요청/응답 body: camelCase
- URL 경로 파라미터: kebab-case
- 쿼리 파라미터: camelCase
- 데이터베이스 필드명은 이 계약에 노출하지 않음

### 옵셔널 필드 처리
- 옵셔널 필드가 없을 때: 키 자체를 생략 (null 대신)
- 명시적으로 null인 경우에만 null 반환 (삭제된 값 등)
- undefined는 JSON 직렬화 시 제거되므로 사용하지 않음

### 날짜/시간
- 모든 날짜: ISO 8601 형식 (`2024-01-15T09:30:00.000Z`)
- 타임존: UTC 기준
- 클라이언트에서 로컬 변환 책임

### 페이지네이션
- 기본 페이지 크기: 20
- 최대 페이지 크기: 100
- 페이지 번호: 1부터 시작

---

## 변경 이력

| 날짜 | 변경 내용 | 변경자 |
|------|-----------|--------|
| {YYYY-MM-DD} | 최초 생성 | {에이전트명} |
