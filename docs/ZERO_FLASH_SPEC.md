# CIC Zero-Flash 설계 지침 (V2→V3 이식)

지휘소 CIC 화면의 모든 깜빡임 제거 및 **Zero-Flash** 구조 유지를 위한 기술 규약.  
V2에서 검증된 원칙을 V3 Warroom/Dashboard에 적용.

---

## 1. 화면 깜빡임 3대 원인 (Technical Sabotage)

| 원인 | 설명 | 대응 |
|------|------|------|
| **무지성 전체 새로고침** | `location.reload()` 등 페이지 전체 리로드 | **금지**. AJAX/WebSocket/SSE만 사용. |
| **FOUC** | 테마가 로드 후 적용되어 잠깐 흰 화면 노출 | **Critical CSS 인라인**: `index.html` `<head>` 내 `#zero-flash-critical` 스타일로 페인트 전 배경 확정. |
| **무한 리렌더** | 상태 하나 바뀔 때마다 전체 트리 리렌더 | **필드별 구독**: 변경된 데이터만 쓰는 컴포넌트만 리렌더. |

---

## 2. 구현 원칙

- **AJAX/WebSocket/SSE**: 데이터만 비동기로 가져오는 Stream 방식. 페이지 전체 reload 코드 없음.
- **CSS Inlining**: 다크 모드 배경(`#050505` 또는 `#0f1419`)을 `index.html` 최상단 `<style id="zero-flash-critical">`에 배치. `theme-color` 메타 통일.
- **Persistent Layout**: 메뉴 이동 시 배경·헤더·사이드바는 고정, 콘텐츠 영역만 교체하는 SPA 구조.
- **주기 갱신**: 30초 이상 권장. 짧은 주기 폴링으로 전체 리렌더 유발 금지.

---

## 3. V3 Warroom 적용 사항

- `/warroom`: 정적 HTML + fetch 기반. **`location.reload()` 미사용**. 스냅샷 갱신은 `setInterval(load, 30000)` (30초).
- **Critical CSS**: `body { background: #0f1419; }` 등 최상단 인라인으로 FOUC 방지.
- **향후 Dashboard (React/Vue 등)**: V2와 동일하게 Layout memo, Worker/Live 전용 Context로 블록별 구독, 전체 리프레시 금지.

---

## 4. 점검 체크리스트

- [ ] 코드베이스에 `location.reload()` / `window.location.reload` 없음
- [ ] `index.html`에 zero-flash용 인라인 스타일 존재, `theme-color` 다크
- [ ] 주기 갱신 30초 이상
- [ ] 고빈도 데이터는 전용 스트림(WebSocket/SSE) 권장

---

## 5. 코드 생성 시 지시 (AI/개발자)

- **`window.location.reload()` 또는 `location.reload()`가 생성되면 즉시 삭제**하고, **fetch 또는 axios로 부분 갱신**하도록 수정한다.
- 전체 페이지 리로드는 금지. 데이터만 주기적으로 가져와서 DOM/상태만 갱신.

---

*정적 화면 위에 흐르는 데이터가 핵심이며, 화면 자체가 깜빡이면 안 된다.*

**참조**: V2 `docs/ZERO_FLASH_SPEC.md`, `docs/Warroom_CIC_Dashboard_점검결과_분석.md`
