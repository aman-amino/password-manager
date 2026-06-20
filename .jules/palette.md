## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - Instant Search and Filtering UX
**Learning:** Users with many vault items benefit significantly from instant, client-side filtering that doesn't require server round-trips. Using ARIA attributes like `aria-pressed` on filter buttons also ensures the UI state is communicated to assistive technologies.
**Action:** Implemented client-side search and scope-based filtering in `frontend/app.js` and added `aria-pressed` states to filter buttons.

## 2026-02-12 - User-Friendly Vault Empty State
**Learning:** A blank screen when no vault items match search or filters provides poor feedback. An explicit "No secrets found" message with an icon improves user confidence and provides clear instruction.
**Action:** Implemented an empty state in the `renderVault` function in `backend/app/static/app/app.js`.

## 2026-06-17 - Keyboard Accessibility for Detail Panes
**Learning:** Interactive side panes and modals should always be dismissible via the 'Escape' key to ensure a standard and accessible micro-UX for keyboard users.
**Action:** Implemented a global 'Escape' key listener in `backend/app/static/app/app.js` to close the secret detail pane.

## 2026-06-18 - Consistent Async Loading Feedback
**Learning:** Micro-UX delight is achieved through consistent visual feedback for all long-running actions. Using Bootstrap spinners with text updates (e.g., 'Signing In...', 'Decrypting...') across all submission and processing buttons improves perceived responsiveness.
**Action:** Implement loading state toggles for all async buttons (Auth, Decrypt, Save) using a consistent `.spinner-border` and `.btn-text` pattern.
