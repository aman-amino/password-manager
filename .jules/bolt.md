## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.
