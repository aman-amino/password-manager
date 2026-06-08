## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - Instant Search and Filtering UX
**Learning:** Users with many vault items benefit significantly from instant, client-side filtering that doesn't require server round-trips. Using ARIA attributes like `aria-pressed` on filter buttons also ensures the UI state is communicated to assistive technologies.
**Action:** Implemented client-side search and scope-based filtering in `frontend/app.js` and added `aria-pressed` states to filter buttons.

## 2026-05-15 - Visual Feedback for Async Actions
**Learning:** Providing immediate visual feedback (like spinners and "Saving..." labels) during asynchronous operations prevents user frustration and potential double-submissions, while making the app feel more responsive.
**Action:** Added a Bootstrap spinner and stateful text to the "Save Secret" button, managed via a `finally` block in JavaScript for robustness.
