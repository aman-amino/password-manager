## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - AccessGrant Query Optimization & Serializer Refactor
**Learning:** Identified N+1 query patterns in `AccessGrantViewSet` due to missing `select_related` on related users and vault items. Also noticed repeated import overhead in `VaultItemSerializer` by importing `base64` inside method scopes.
**Action:** Added `select_related("grantee", "vault_item", "granted_by")` to the queryset and moved `base64` import to module level.

## 2026-02-12 - User List Query Optimization
**Learning:** The user list endpoint was susceptible to N+1 queries when accessing organization and department names during serialization.
**Action:** Added `select_related('organization', 'department')` to the `UserViewSet.get` method in `backend/vault/auth_views.py`.

## 2026-02-12 - DOM Batching with DocumentFragment
**Learning:** In a vanilla JS application, frequent DOM manipulations (like  in a loop) cause multiple reflows. Batching these updates using  significantly improves UI responsiveness for large lists.
**Action:** Always use  when rendering lists or multiple elements to the DOM in a loop.

## 2026-06-14 - DOM Batching with DocumentFragment
**Learning:** In a vanilla JS application, frequent DOM manipulations (like appendChild in a loop) cause multiple reflows. Batching these updates using DocumentFragment significantly improves UI responsiveness for large lists.
**Action:** Always use DocumentFragment when rendering lists or multiple elements to the DOM in a loop.
