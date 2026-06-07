## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - Instant Search and Filtering UX
**Learning:** Users with many vault items benefit significantly from instant, client-side filtering that doesn't require server round-trips. Using ARIA attributes like `aria-pressed` on filter buttons also ensures the UI state is communicated to assistive technologies.
**Action:** Implemented client-side search and scope-based filtering in `frontend/app.js` and added `aria-pressed` states to filter buttons.

## 2026-05-20 - Async Action Visual Feedback
**Learning:** For asynchronous operations like saving a secret, providing immediate visual feedback (disabling the button and showing a spinner) is essential for a responsive feel and to prevent duplicate submissions. Using a `finally` block in JavaScript ensures the UI is always restored to a consistent state regardless of the operation outcome.
**Action:** Implemented a loading spinner and "Saving..." text for the `#saveSecretBtn` in `backend/app/static/app/app.js`.
