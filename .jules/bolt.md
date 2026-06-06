## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - AccessGrant Query Optimization & Serializer Refactor
**Learning:** Identified N+1 query patterns in `AccessGrantViewSet` due to missing `select_related` on related users and vault items. Also noticed repeated import overhead in `VaultItemSerializer` by importing `base64` inside method scopes.
**Action:** Added `select_related("grantee", "vault_item", "granted_by")` to the queryset and moved `base64` import to module level.

## 2026-06-06 - User List Query Optimization
**Learning:** Identified N+1 query pattern in `UserViewSet.get` where organization and department names were accessed per user. Also found that checking `request.user.organization` triggers a query while `request.user.organization_id` does not if the ID is already in the session/user object.
**Action:** Added `select_related("organization", "department")` and switched to `organization_id` check. Reduced queries from 22 to 1 for 11 users.
