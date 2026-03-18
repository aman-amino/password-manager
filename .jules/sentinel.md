## 2025-05-15 - [Visibility Gap: Unlogged Security Actions]
**Vulnerability:** Critical security actions (Admin URL rotation, Login, Unauthorized admin access) were not being logged in the audit trail.
**Learning:** Even with an audit log system in place, it's easy to overlook system-level events (like rotations) or middleware-level events (like blocked access) that aren't tied to standard model CRUD operations.
**Prevention:** Explicitly map all security-sensitive state transitions and access control failures to audit events during the design phase.

## 2025-05-15 - [CSRF Risk in State-Changing View]
**Vulnerability:** `rotate_admin_url` used GET instead of POST, making it vulnerable to CSRF.
**Learning:** Any view that performs side effects (especially security-critical ones like rotating access tokens) MUST use POST and be protected by CSRF middleware.
**Prevention:** Audit all views for HTTP method compliance. Use `@require_POST` for all state-changing operations.

## 2025-05-15 - [WebCrypto Derivation Misuse]
**Vulnerability:** Incorrect HKDF key derivation from PBKDF2 in `frontend/crypto.js`.
**Learning:** WebCrypto `deriveKey` has specific expectations for the output key type. When chaining KDFs (PBKDF2 -> HKDF), it's often more reliable to use `deriveBits` for the intermediate secret.
**Prevention:** Use standard, tested cryptographic libraries where possible, and always verify derivation logic against official WebCrypto examples.

## 2025-05-15 - [Temporal Authorization Failure]
**Vulnerability:** Access grants were checked for activity status but not for expiration time in `vault/policy.py`.
**Learning:** Time-based access control must explicitly check current system time against expiration fields in all authorization paths (both individual object checks and queryset filtering).
**Prevention:** Implement a central helper for checking grant validity that includes both active status and temporal constraints.
