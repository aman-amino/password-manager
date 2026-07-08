## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - AccessGrant Query Optimization & Serializer Refactor
**Learning:** Identified N+1 query patterns in `AccessGrantViewSet` due to missing `select_related` on related users and vault items. Also noticed repeated import overhead in `VaultItemSerializer` by importing `base64` inside method scopes.
**Action:** Added `select_related("grantee", "vault_item", "granted_by")` to the queryset and moved `base64` import to module level.

## 2026-02-12 - User List Query Optimization
**Learning:** The user list endpoint was susceptible to N+1 queries when accessing organization and department names during serialization.
**Action:** Added `select_related('organization', 'department')` to the `UserViewSet.get` method in `backend/vault/auth_views.py`.

## 2026-06-17 - ForeignKey ID Optimization in Filters
**Learning:** In Django querysets, filtering by `related_field_id=obj.id` is more efficient than `related_field=obj` as it avoids an implicit query to fetch the related object if it's not already prefetched.
**Action:** Updated `vault_item_queryset_for_user` in `backend/vault/policy.py` to use `organization_id` and `department_id` for filtering.

## 2026-06-18 - Redundant Query Elimination and DRF BinaryField Optimization
**Learning:** Redundant database queries occur when assigning model instances to foreign keys if the ID is already available (e.g., `user.organization_id`). Additionally, DRF `ModelSerializer` can handle Base64 for `BinaryField` automatically if `extra_kwargs` explicitly sets `read_only: False`.
**Action:** Optimized `VaultItemSerializer.create` and `log_audit_event` to use `_id` fields. Pruned unnecessary `select_related` in viewsets. Removed manual Base64 logic in `VaultItemSerializer` by configuring `extra_kwargs`.

## 2026-06-20 - Client-Side Tab Data Caching
**Learning:** Redundant API calls when switching between application tabs (Shared, People, Audit) cause unnecessary network overhead and UI lag.
**Action:** Implemented a client-side caching mechanism in `app.js` that stores API results and invalidates them only after relevant create/share actions.

## 2026-06-21 - Vault Rendering Optimization (Event Delegation & Date Caching)
**Learning:** Attaching multiple event listeners to large lists (vault cards) increases memory overhead and slows down DOM updates. Additionally, re-calculating date strings during every render/filter cycle is redundant.
**Action:** Implemented event delegation on the vault grid and cached formatted date strings on the secret objects during the initial fetch.
