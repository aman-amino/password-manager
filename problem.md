# Security Findings

## 1. Missing Audit Logs for Security Events [FIXED]
**Description:** Successful logins, admin URL rotations, and unauthorized admin access attempts were not logged in the AuditEvent table.
**Impact:** Difficulty in investigating security incidents and monitoring for brute-force or unauthorized access patterns.
**Fix:** Implemented signal receivers for login, added logging to rotation views, and updated middleware to log unauthorized attempts.

## 2. Admin URL Rotation via GET Request [FIXED]
**Description:** The `rotate_admin_url` endpoint changes server state (deactivates old tokens, creates new ones) but was accessible via a GET request.
**Impact:** Vulnerable to Cross-Site Request Forgery (CSRF). An attacker could trick a logged-in superadmin into visiting a URL that rotates their admin link, potentially locking them out or causing denial of service.
**Fix:** Converted the view to require POST requests and added CSRF token validation in the frontend.

## 3. Broad Token Extraction in AdminTokenMiddleware
**Description:** The middleware extracts the admin token from any path segment starting with `admin_`.
**Impact:** While not immediately exploitable, it's a loose pattern that could lead to unexpected behavior if users create resources with names starting with `admin_`.
**Priority:** Low

## 4. WebCrypto HKDF Misconfiguration
**Description:** In `frontend/crypto.js`, `deriveRootKey` uses HKDF as the target key type for PBKDF2 derivation.
**Impact:** HKDF is usually an intermediate step or used for salt/info. Deriving an HKDF "key" to then derive further keys might be non-standard or incorrect depending on intended use.
**Priority:** Medium
