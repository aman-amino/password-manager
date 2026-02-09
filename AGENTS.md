# Agent State Log - Django Password Manager

## Project: Maximum-Security Zero-Knowledge Password Manager

**Started:**   
**Location:** d:\password\new-manager 
**Status:** Step 4 complete

## Session History

### Session 1: 
**Status:** Step 1 completed  
**Current Step:** 1/9  
**Final Action:** Documented threat model and security goals; initialized project trackers.  

**Project Summary:**
- Zero-knowledge password manager with client-side cryptography and strict role-based access.
- Admin access is gated by per-request random admin URL minted by superadmin.

### Session 2: 
**Status:** Environment setup updates  
**Current Step:** 1/9  
**Final Action:** Pinned backend requirements to latest versions; created `.venv` (pip bootstrap failed due to temp permissions).  

### Session 3: 
**Status:** Requirements recheck  
**Current Step:** 1/9  
**Final Action:** Rechecked package versions; updated Gunicorn to latest stable release.  

### Session 4: 
**Status:** Requirements verified  
**Current Step:** 1/9  
**Final Action:** Verified latest stable versions on PyPI; pinned Gunicorn to 25.0.3.  

### Session 5: 
**Status:** Step 2 completed  
**Current Step:** 2/9  
**Final Action:** Documented cryptography design and primitives.  

### Session 6: 
**Status:** Step 3 completed  
**Current Step:** 3/9  
**Final Action:** Documented data model for Django/Postgres.  

### Session 7: 
**Status:** Step 4 completed  
**Current Step:** 4/9  
**Final Action:** Documented authorization and policy engine rules.  


---

## Progress Tracker

- [x] Step 0: set up project structure and dependencies 
- [x] Step 1: Threat model + security goals 
- [x] Step 2: Cryptography design 
- [x] Step 3: Data model (Django/Postgres) 
- [x] Step 4: Authorization + policy engine 
- [ ] Step 5: API design 
- [ ] Step 6: Browser crypto module 
- [ ] Step 7: Frontend flows 
- [ ] Step 8: Hardening checklist 
- [ ] Step 9: Verification 

---

## Architecture Decisions

### Stack
- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** WebCrypto API (vanilla JS/React TBD)
- **Crypto:** Client-side only (zero-knowledge)

### Key Principles
1. Server never sees plaintext secrets
2. All encryption/decryption in browser
3. Cryptographic enforcement of "personal" secrets
4. Audit logging for all operations
5. Least privilege access control
6. admin panel should be modern and user-friendly like chatgpt
7. django admin panel should be hidden from regular users using token based admin link creation like /admin_{random_string}, it's url should be random and it will create a new random url every time the superadmin ask to access admin panel (like in superadmin pnal there is option to access django admin panel, which upon clicking it will generate a random url and redirect to it, and it should be create whenever superadmin clicks on it)

---

## Current State

**Virtual Environment:** `.venv` (pip bootstrap failed due to temp permission error)
**Django Project:** Initialized (Core apps: `vault`, `app`)
**Database:** SQLite for development, PostgreSQL-ready
**Dependencies:** Pinned to latest stable versions in `backend/requirements.txt`

## rules
1. Always use the latest version of Django and Django REST Framework
2. Always use the latest version of PostgreSQL
3. Always use the latest version of WebCrypto API
4. Always use the latest version of AES-256-GCM
5. Always use the latest version of PBKDF2
6. Always use the latest version of Django Axes
7. Always use the latest version of Django CSP
8. Always use the latest version of Django Admin
9. Always use the latest version of Django REST Framework
10. Make sure to use final-access-matrix.md to verify the security of the application
11. always update AGENTS.md with the latest information
12. always update progress-tracker.md with the latest information, each step should be in a new line and should be in the format of - [ ] step description
13. always update architecture-decisions.md with the latest information
14. always update current-state.md with the latest information
15. always update notes-and-decisions.md with the latest information
16.  readme.md should be updated with the latest information
17. ui always use latest version of bootstrap
18. look of the application should be modern and user-friendly like chatgpt  
19. auto manage git, commit and push after every step
20. always update session-history.md with the latest information, which keep each session in a new line and should be in the format of Session X: YYYY-MM-DD HH:MM then status, highlights, Where to find changes.
21. always follow proper management of files and folders
---

## Notes & Decisions

- Step 1 threat model and security goals documented in `notes-and-decisions.md`.
- Backend requirements pinned; venv created with pip bootstrap issue noted in `notes-and-decisions.md`.
- Requirements rechecked; Gunicorn updated to latest stable version.
- Latest stable versions verified via PyPI; Gunicorn pinned to `25.0.3`.
- Step 2 cryptography design documented in `notes-and-decisions.md`.
- Step 3 data model documented in `notes-and-decisions.md`.
- Step 4 authorization and policy engine documented in `notes-and-decisions.md`.
