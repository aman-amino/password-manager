## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-05-31 - State and Context Accessibility
**Learning:** Filter chips and navigation links often lack state indication (e.g., `aria-pressed`, `aria-current`), making it difficult for screen readers to convey the current application state.
**Action:** Implement `aria-pressed` for toggleable filters and `aria-current="page"` for active navigation links in `app.js`.
