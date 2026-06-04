## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - AccessGrant Query Optimization & Serializer Refactor
**Learning:** Identified N+1 query patterns in `AccessGrantViewSet` due to missing `select_related` on related users and vault items. Also noticed repeated import overhead in `VaultItemSerializer` by importing `base64` inside method scopes.
**Action:** Added `select_related("grantee", "vault_item", "granted_by")` to the queryset and moved `base64` import to module level.

## 2026-06-04 - User List Query Optimization
**Learning:** `UserViewSet.get` was suffering from an N+1 query bottleneck. While iterating through users to build the response data, it accessed the `name` attribute of related `organization` and `department` objects, triggering a new database query for every user.
**Action:** Applied `select_related('organization', 'department')` to the User queryset to pre-fetch these relations using a SQL join, significantly improving performance for organization-wide user listings.
