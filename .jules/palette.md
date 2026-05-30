## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - [Navigation State Accessibility]
**Learning:** For single-page applications or UI components that toggle views (like a sidebar), simply adding an "active" class isn't enough for assistive technology.
**Action:** Use `aria-current="page"` to programmatically signal the active state to screen readers and update it on click.
