## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - Instant Search and Filtering UX
**Learning:** Users with many vault items benefit significantly from instant, client-side filtering that doesn't require server round-trips. Using ARIA attributes like `aria-pressed` on filter buttons also ensures the UI state is communicated to assistive technologies.
**Action:** Implemented client-side search and scope-based filtering in `frontend/app.js` and added `aria-pressed` states to filter buttons.

## 2026-06-04 - User-Friendly Empty States
**Learning:** A blank screen during filtered searches or in an empty vault provides poor feedback and can be mistaken for a loading failure or application bug. Providing a visual anchor (icon) and clear instructions improves perceived reliability.
**Action:** Added a "No secrets found" empty state to the `renderVault` function in `app.js`, including a material icon and guidance for the user.
