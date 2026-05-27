# Current State

- Virtual environment created: `.venv` (pip bootstrap failed due to temp permission error)
- Django project scaffolded under `backend/config` with core apps: `vault`, `app`
- Database configured: SQLite for development, PostgreSQL-ready
- Dependencies pinned to latest stable versions (checked 2026-02-09) in `backend/requirements.txt`
- Step 1 complete: Threat model and security goals documented
- Step 2 complete: Cryptography design documented
- Step 3 complete: Data model documented
- Step 4 complete: Authorization and policy engine documented
- Backend code scaffolded (settings, URLs, health check)
- Core auth models implemented (Organization, Department, User)
- Key material models implemented (UserKeyMaterial, ScopeKey, VaultItem, VaultItemKey)
- Data model extensions implemented (Tag, AccessGrant, RecoveryKey, AuditEvent)
- Policy engine implemented (vault item authorization and queryset filters)
- API endpoints implemented for vault items
- Browser crypto module implemented (WebCrypto helpers)
- Frontend flows scaffolded (static admin UI)
- Hardening checklist added
- Verification checklist added
- CSP and Axes settings updated to current versions
- Root endpoint added and static serving enabled in DEBUG
- Django UI scaffold added for ChatGPT-like admin experience
- CSP updated for Bootstrap/Fonts and static URL fixed
- Next steps documented in `notes-and-decisions.md`
- Collected static files are ignored (`backend/staticfiles/`)
- Documentation trackers initialized
- Step 10 complete: Security enhancements and bug fixes
    - Audit logging integrated into VaultItemViewSet
    - Rotating admin URL implemented with `AdminConfig` and `AdminTokenMiddleware`
    - Superadmin visibility fixed in policy engine
    - Security settings hardened for production
    - Backend tests added for core security logic

- Fixed DJANGO_SETTINGS_MODULE in docker-compose.yml.
- Fixed class shadowing in backend/app/apps.py.
- Created .env file for local development.
## Step 11: Production Readiness
- Query performance optimized for VaultItem API.
- MFA support implemented (TOTP secret storage and verification view).
- Audit logging expanded to auth failures and logouts.
- Modern UI integrated based on Stitch design.
## Step 12: MFA Enforcement and Permission Refactor
- Centralized policy engine enforcement of role permissions.
- Refactored object-level checks to align with access matrix.
## Step 13: Secure Context Handling & UI Contrast Polish
- Added check for SubtleCrypto and Secure Context (`window.isSecureContext`) with clear guidance error message.
- Re-styled login/registration form labels, form text, and inputs with high-contrast, premium dark mode styling.
