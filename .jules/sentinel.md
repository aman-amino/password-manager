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

## 2025-05-15 - [Privilege Escalation in Hierarchical RBAC]
**Vulnerability:** Subadmins could access organization-wide items if those items happened to be associated with their department.
**Learning:** Hierarchical roles must be strictly scoped. Just because a user has a "management" role within a sub-unit (department), it doesn't mean they should manage items whose scope belongs to the parent unit (organization).
**Prevention:** Always verify that both the user's scope (department) AND the item's intended scope (DEPT vs ORG) match before granting access based on a sub-administrative role.

## 2025-05-15 - [API Surface Hardening]
**Vulnerability:** Several high-level configurations (Rate limiting, Basic Auth, Cookie SameSite, Payload limits) were missing or set to insecure defaults.
**Learning:** Default framework settings (like DRF's Basic Auth or Django's Lax cookies) are often optimized for developer convenience rather than maximum security.
**Prevention:** Always explicitly configure security-sensitive headers and framework features (throttling, auth backends, payload validation) to match the project's specific threat model.

## 2025-05-15 - [Defense in Depth: Admin URL vs RBAC]
**Vulnerability:** Relying solely on the "secret" admin URL for security allowed any staff user who obtained the URL to access the admin panel.
**Learning:** Obscurity (secret URLs) is a valid layer of defense but must never replace standard authorization (RBAC).
**Prevention:** Always verify the user's role/permissions even when they provide a secret token or access a hidden endpoint.

## 2026-02-09 - [Scope Escalation in Resource Creation]
**Vulnerability:** Resource creation (VaultItem) lacked role-based scope validation, allowing regular users to create items in ORG/DEPT scopes despite being unable to view them.
**Learning:** Object-level permissions and queryset filtering do not implicitly protect the `create` path. Input fields that dictate resource visibility or ownership must be validated against the actor's role.
**Prevention:** Use DRF `has_permission` or serializer validation to strictly enforce role-based constraints on "owner" or "scope" fields during creation.

## 2026-02-10 - [Permission Redundancy and Shadowing]
**Vulnerability:** Multiple conflicting definitions of the same permission class (`CanCreateVaultItem`) existed in the same file.
**Learning:** Python allows re-definition of classes, where the last definition shadows previous ones. This can lead to security bypasses if an earlier, stricter definition is overwritten by a later, looser one without the developer noticing.
**Prevention:** Consolidate permission logic into a single class or use distinct names. Always audit permission files for duplicate class or function names.

## 2026-02-10 - [Session-Based MFA Enforcement Pattern]
**Vulnerability:** Users with MFA enabled could still access sensitive vault operations if they only completed primary authentication (e.g. session hijacking or password compromise).
**Learning:** MFA should be enforced not just at login, but at the API layer for sensitive resources. By comparing `last_mfa_login` with `last_login`, we ensure that the second factor was provided for the current session.
**Prevention:** Implement a standard `RequiresMFA` permission class and apply it to all viewsets handling sensitive data (secrets, keys, etc.).
