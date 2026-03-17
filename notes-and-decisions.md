# Notes And Decisions

## Threat Model (Step 1)
- Primary assets: encrypted secrets, client master keys, org metadata, audit logs.
- Trust boundaries: browser vs backend API vs database.
- Adversaries: external attackers, malicious insiders, compromised clients, credential stuffing.
- Key assumptions: TLS enforced; browsers provide WebCrypto; users protect devices.

## Security Goals
- Zero-knowledge: server never learns plaintext secrets or master keys.
- Integrity: tamper-evident storage and audit logging for all secret operations.
- Least privilege: role-based access aligned with final-access-matrix.md.
- Admin minimization: hidden admin URL generated on demand by superadmin only.
- Secure defaults: deny by default, explicit access grants, rate limiting.

## Open Questions
- Policy engine representation for department scoping and owner-only secrets.
- How to handle emergency recovery without breaking zero-knowledge guarantees.

## Environment Notes
- Pinned backend dependencies to latest versions on 2026-02-09 in `backend/requirements.txt`.
- `python -m venv .venv` succeeded, but `ensurepip` failed due to temp folder permission errors.
- Rechecked package versions on 2026-02-09; Gunicorn pinned to `25.0.3`.
- Added root endpoint and dev static serving to reduce 404s during local runserver.
- Added ChatGPT-like Django UI scaffold using Bootstrap 5.3.3.
- Updated CSP to allow Bootstrap CDN and Google Fonts; fixed STATIC_URL for dev static serving.

## Cryptography Design (Step 2)
- Client-side only: all encryption and decryption happens in the browser via WebCrypto.
- Password KDF: PBKDF2-HMAC-SHA-256 with per-user random salt and high iteration count stored server-side.
- Master key derivation: PBKDF2 output -> root key; subkeys derived with HKDF-SHA-256 for separation.
- Data encryption: AES-256-GCM with per-item random 96-bit nonce.
- Envelope encryption: each secret uses a random 256-bit data key; data key is wrapped by key-encryption keys.
- Key-encryption keys: derived from user root key for personal secrets; org/dept secrets have scope keys.
- Multi-recipient sharing: data key wrapped per authorized recipient using ECDH (P-256) + AES-GCM.
- Integrity: AES-GCM provides confidentiality and integrity; tampering yields authentication failure.
- Key rotation: rotate scope keys periodically; rewrap data keys without re-encrypting ciphertext.
- Recovery: optional recovery key pair stored client-side; server stores only wrapped data keys.

## Data Model (Step 3)
- User: auth identity with role, status, MFA flags, and org membership.
- Organization: root container for users, departments, and shared secrets.
- Department: organizational sub-scope for dept-wide secrets and access boundaries.
- VaultItem: encrypted secret blob with metadata (title, type, favorite, timestamps).
- VaultItemKey: per-recipient wrapped data key for each VaultItem.
- ScopeKey: encrypted wrapping keys per org/dept scope, rotated and versioned.
- UserKeyMaterial: stores salt, KDF params, and encrypted user key bundles.
- RecoveryKey: optional recovery key public material + wrapped recovery data key.
- AuditEvent: immutable security log for access, changes, admin actions.
- Tag: system tags (admin-managed) and personal tags (owner-managed).
- AccessGrant: explicit non-owner access with scope and expiry for shared secrets.

## Authorization + Policy Engine (Step 4)
- Authorization is centralized in a policy engine; all API endpoints call policy checks.
- Roles: Superadmin, Admin, Subadmin, Regular User.
- Enforced matrix: `final-access-matrix.md` is the source of truth for resource access.
- Default deny: any action not explicitly allowed by policy is rejected.
- Ownership rule: personal secrets are owner-only regardless of role.
- Dept scope: Subadmin access limited to own department; Admin can access all departments.
- Org scope: Superadmin/Admin can access org-wide non-personal secrets.
- System tags: Superadmin/Admin manage; others read-only.
- Recovery/reset actions: only Superadmin/Admin for allowed roles per matrix.
- Sharing: AccessGrant required for any non-owner access; grants are time-bound and auditable.
- Enforcement points: API layer, queryset filtering, and object-level permission checks.

## Backend Scaffold (Step 0/1 Implementation)
- Created Django project scaffold under `backend/config` with `manage.py`.
- Added core apps `app` and `vault` with placeholder models.
- Configured security middleware: SecurityMiddleware, Axes, CSP, and Whitenoise.
- Added `/health/` endpoint for basic service liveness checks.
- Implemented core auth data model: Organization, Department, and custom User with role and MFA flag.

## Step 2 Implementation (Key Material Models)
- Added `UserKeyMaterial` for KDF params and encrypted user key bundle.
- Added `ScopeKey` for org/dept wrapping keys with versioning.
- Added `VaultItem` and `VaultItemKey` for encrypted secrets and per-recipient wrapped keys.

## Step 3 Implementation (Data Model)
- Added Tag and VaultItemTag for system/personal tagging.
- Added AccessGrant for explicit non-owner sharing.
- Added RecoveryKey for optional recovery flows.
- Added AuditEvent for immutable security logs.

## Step 4 Implementation (Authorization + Policy Engine)
- Added policy engine with explicit `can_view`/`can_manage` decisions and reasons.
- Enforced personal secrets owner-only in policy and queryset filters.
- Added DRF object-level permission helper for vault items.

## Step 5 Implementation (API Design)
- Added VaultItem API endpoints with DRF ViewSet.
- Added serializer with server-side ownership/org scoping.
- Wired API under `/api/vault-items/`.

## Step 6 Implementation (Browser Crypto Module)
- Added WebCrypto utility module with PBKDF2, HKDF, AES-256-GCM helpers.
- Included base64 and UTF-8 helpers for client-side data handling.

## Step 7 Implementation (Frontend Flows)
- Added initial admin-style frontend layout with vault list, detail, and access request flows.
- Implemented sidebar navigation and card-based secret grid.

## Step 8 Implementation (Hardening Checklist)
- Added `hardening-checklist.md` with security and deployment hardening items.

## Step 9 Implementation (Verification)
- Added `verification.md` with security, crypto, backend, and UI verification items.

## Next Steps
- Wire UI to live API data (vault list, detail, filters).
- Add auth flow for UI and API (login, CSRF, session handling).
- Create secret modal with WebCrypto integration.
- Implement share/revoke UI for AccessGrant.
- Added audit log view using AuditEvent. (Mock UI only, API logging implemented in Step 10)
- Implement rotating admin URL for superadmin. (Implemented in Step 10)
- Add tests for policy engine and API permissions. (Implemented in Step 10)
- Keep `backend/staticfiles/` out of git; use `collectstatic` only for deployment.

## Security Enhancements and Bug Fixes (Step 10)
- Audit Logging: Integrated `log_audit_event` into `VaultItemViewSet` for all CRUD actions.
- Rotating Admin URL:
    - Added `AdminConfig` model to store active admin tokens.
    - Added `AdminTokenMiddleware` to enforce token-based access to `/admin_.../` paths.
    - Added `rotate_admin_url` view for superadmins to generate new tokens.
- Superadmin Visibility: Updated policy engine to allow superadmins access to all non-personal items across organizations.
- Refined Permissions: Introduced `CanManageVaultItem` DRF permission class for cleaner object-level checks.
- Hardened Settings: Updated `settings.py` with HSTS, secure cookies, and SSL redirect defaults for non-debug environments.
- Verification: Added comprehensive backend tests in `backend/vault/tests.py` covering policy, audit logging, and admin rotation.

## Final Refinements and Production Roadmap (Step 11)
- Admin Token Middleware: Updated to use `path.startswith` and more strict splitting to avoid false positives.
- Admin Rotation: View now requires POST method for security; UI (app.js) updated to call this securely with CSRF.
- Bulk Auditing: Added audit logging for list operations to track broad vault access.
- Production Roadmap: Created `production-upgrade-plan.md` to guide future development.

## Environment Notes
- Updated django-csp settings to new `CONTENT_SECURITY_POLICY` format.
- Added Axes authentication backend and removed deprecated settings.
