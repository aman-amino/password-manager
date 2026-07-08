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

## 2026-06-19 - Micro-UX feedback for async operations
**Learning:** Providing immediate visual feedback (spinners and stateful button text) for long-running operations like authentication and decryption significantly improves perceived performance and user confidence.
**Action:** Implemented loading states for login and decryption buttons and added a password visibility toggle.

## 2026-06-20 - Auto-focus for Modals and Auth Forms
**Learning:** Users expect the cursor to be ready in the first input field when a modal or authentication form appears. Manual clicking increases friction.
**Action:** Implemented auto-focus using Bootstrap `shown.bs.modal` events for secret creation/sharing modals and focused the username field on auth form load and tab switch.

## 2026-06-21 - Vault Card Accessibility & Empty State UX
**Learning:** Simple interactive divs without ARIA roles or keyboard support are inaccessible to screen reader and keyboard-only users. A blank screen when no items match search/filters is confusing.
**Action:** Added 'button' role, tabindex, and aria-labels to vault cards. Implemented Enter/Space key listeners and a descriptive empty state for the vault view.
