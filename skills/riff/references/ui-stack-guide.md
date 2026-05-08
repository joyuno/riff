# UI 스택 가이드

이 파일은 Riff 0의 UI 스택 확정 시, 그리고 BUILD-EXECUTE 에이전트가 라이브러리를 선택할 때만 읽는다. SKILL.md에 포함하지 않는다.

---

## 스택 선택 기준

질문 예산 A/B면 사용자에게 확인. C/D면 프레임워크 자동 감지 후 기본값 적용.

**프레임워크 감지:**
- `package.json` + React/Next.js → shadcn/ui + Tailwind + Motion
- `pubspec.yaml` + Flutter → Material 3 + flutter_animate
- React Native → RN Paper + Reanimated

**UI 개성 수준:**
- 표준 (빠른 개발): Tier 1만
- 고퀄리티 (차별화): Tier 1 + Tier 2 혼합

---

## React/Next.js 라이브러리 티어

| 티어 | 라이브러리 | 역할 | Context7 |
|------|-----------|------|----------|
| 1 | shadcn/ui + CVA | 기본 컴포넌트 전체 | 가능 |
| 1 | Tailwind CSS v4 | 유틸리티 스타일링 | 가능 |
| 1 | Motion (motion/react) | 트랜지션, 애니메이션, 제스처 | 가능 |
| 2 | Origin UI | 400+ 고퀄 컴포넌트, 접근성 완비 | 가능 |
| 2 | Aceternity UI | 마그네틱·3D 카드 등 임팩트 섹션 | 가능 |
| 2 | Magic UI | 랜딩 블록, 파티클, Shimmer | 가능 |
| 2 | Animata | 핸드크래프트 애니메이션 컴포넌트 | 가능 |
| 3 | Rive | 상태 머신 인터랙티브 에셋 (디자이너 협업 필수) | 가능 |
| 3 | GSAP | 복잡 스크롤 시퀀스, 마케팅 페이지 | 가능 |

## Flutter 라이브러리 티어

| 티어 | 라이브러리 | 역할 | 조회 |
|------|-----------|------|------|
| 1 | Material 3 | 기본 위젯 + 테마 시스템 | 가능 |
| 1 | flutter_animate | `.animate()` 체이닝 애니메이션 | 가능 |
| 2 | Rive Flutter | Web과 동일 `.riv` 에셋 재활용 | 가능 |
| 2 | Lottie Flutter | AE 기반 에셋 재생 | 가능 |
| 2 | animations (Google) | Container Transform, Shared Axis | 가능 |

---

## ui-stack.md 형식

```markdown
# UI 스택 계약

## 프레임워크
[React/Next.js | Flutter | React Native]

## 채택 라이브러리
### Tier 1 (필수)
- shadcn/ui, Tailwind CSS v4, Motion

### Tier 2 (선택 섹션별)
- Origin UI: 폼·테이블
- Aceternity UI: 히어로 섹션, CTA

## 적용 규칙
- Tier 1에 있는 컴포넌트를 직접 구현하지 않는다
- Tier 2 사용 시 Context7로 최신 API 조회 후 구현한다
- Rive/Lottie 에셋은 코드로 생성하지 않는다 (디자이너 산출물)

## 금지
- 임의 색상값 하드코딩 (Tailwind 토큰 또는 CSS 변수만)
- inline style
- 라이브러리에 이미 있는 컴포넌트 재발명
```
