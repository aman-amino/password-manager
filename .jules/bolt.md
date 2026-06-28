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

## 2026-06-28 - Redundant Serializer and Queryset Joins
**Learning:** Django REST Framework's `BinaryField` handles Base64 re-encoding if not careful, and `select_related` can introduce unnecessary JOINs if the related fields are only used as PrimaryKey IDs in the serializer.
**Action:** Use `isinstance(..., bytes)` checks in serializers and remove redundant `select_related` calls for PK-only fields.
