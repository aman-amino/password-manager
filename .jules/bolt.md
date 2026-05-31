## 2025-05-14 - AuditEvent Query Optimization
**Learning:** Found that `AuditEvent` queries filtered by `target_type` and `target_id` were likely slow due to missing indexes. Also identified N+1 query patterns in the `AuditEvent` list API.
**Action:** Add composite index and `select_related` to improve database performance for audit logs.

## 2026-05-31 - Rendering and Query Optimization
**Learning:** Found that clearing and rebuilding a grid with multiple `appendChild` calls in JavaScript causes unnecessary reflows. Also identified that `select_related` can be further optimized by removing joins for fields that are only serialized as primary keys.
**Action:** Use `DocumentFragment` for batch DOM updates in `app.js` and refine `select_related` in Django views based on serializer field requirements.
