## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - AccessGrant Query Optimization & Serializer Refactor
**Learning:** Identified N+1 query patterns in `AccessGrantViewSet` due to missing `select_related` on related users and vault items. Also noticed repeated import overhead in `VaultItemSerializer` by importing `base64` inside method scopes.
**Action:** Added `select_related("grantee", "vault_item", "granted_by")` to the queryset and moved `base64` import to module level.

## 2026-05-20 - UserViewSet N+1 Optimization
**Learning:** The `UserViewSet.get` method was triggering N+1 queries by accessing `u.organization.name` and `u.department.name` for every user in the list. Additionally, using `request.user.organization` in a filter triggers a lookup of the organization object, whereas `request.user.organization_id` is already available on the user object.
**Action:** Added `select_related("organization", "department")` to the user queryset and used `organization_id` for filtering.
