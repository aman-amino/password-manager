## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-02-12 - [Query Optimization with Exists]
**Learning:** For complex authorization checks (like access grants), using `Exists` subqueries with `OuterRef` is significantly more efficient than evaluating a list of IDs and using `id__in`.
**Action:** Refactor `vault_item_queryset_for_user` to use `Exists` for grant verification.
