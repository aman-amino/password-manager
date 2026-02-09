# Architecture Decisions

## Stack
- Backend: Django + Django REST Framework
- Database: PostgreSQL (SQLite only for local dev bootstrap)
- Frontend: WebCrypto API (vanilla JS or React TBD)
- Crypto: Client-side only (zero-knowledge)
- UI: Bootstrap (latest) with modern, ChatGPT-like admin UX
- Dependencies are pinned to latest stable versions in `backend/requirements.txt` (checked 2026-02-09).

## Security Model
- Server never sees plaintext secrets; encryption and decryption are browser-only.
- Personal secrets are cryptographically bound to the owner and are not accessible by role escalation.
- Audit logging for all read/write operations on secrets and role changes.
- Crypto primitives: PBKDF2-HMAC-SHA-256, HKDF-SHA-256, AES-256-GCM, ECDH P-256 for key wrapping.
- Secrets use envelope encryption with per-item data keys and scope-specific wrapping keys.

## Admin Access
- Django admin is hidden behind per-request random URL tokens.
- Only superadmin can mint a new admin URL; each request generates a new random URL.

## Access Control
- Role permissions align with final-access-matrix.md and are enforced in policy checks.
- Least privilege by default; explicit grants required for any cross-user access.

## Data Model
- Org -> Dept -> User hierarchy for scoping.
- VaultItem stores encrypted blobs; VaultItemKey stores per-recipient wrapped data keys.
- ScopeKey stores encrypted org/dept wrapping keys with rotation metadata.
- AuditEvent provides immutable security logs.
