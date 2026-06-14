## 2025-05-14 - Accessibility Improvements
**Learning:** Initial audit of the frontend showed several interactive elements (search input, action buttons) lacked `aria-label` attributes, which hinders screen reader accessibility.
**Action:** Add semantic ARIA labels to key interactive elements in `frontend/index.html`.

## 2026-02-12 - Instant Search and Filtering UX
**Learning:** Users with many vault items benefit significantly from instant, client-side filtering that doesn't require server round-trips. Using ARIA attributes like `aria-pressed` on filter buttons also ensures the UI state is communicated to assistive technologies.
**Action:** Implemented client-side search and scope-based filtering in `frontend/app.js` and added `aria-pressed` states to filter buttons.

## 2026-02-12 - User-Friendly Vault Empty State
**Learning:** A blank screen when no vault items match search or filters provides poor feedback. An explicit "No secrets found" message with an icon improves user confidence and provides clear instruction.
**Action:** Implemented an empty state in the `renderVault` function in `backend/app/static/app/app.js`.

## 2026-02-12 - In-UI Secret Decryption and Copy Feedback
**Learning:** Using  for displaying sensitive information like decrypted secrets is disruptive and provides poor UX. An in-page secure display with immediate "Copy to Clipboard" functionality and visual confirmation (e.g., "Copied!") is much more fluid and professional.
**Action:** Replace  with specific UI components for data display and provide transient visual feedback for clipboard actions.

## 2026-06-14 - In-UI Secret Decryption and Copy Feedback
**Learning:** Using alert() for displaying sensitive information like decrypted secrets is disruptive and provides poor UX. An in-page secure display with immediate "Copy to Clipboard" functionality and visual confirmation (e.g., "Copied!") is much more fluid and professional.
**Action:** Replace alert() with specific UI components for data display and provide transient visual feedback for clipboard actions.
