# Security Findings

## 1. Missing Audit Logs for Security Events [FIXED]
**Description:** Successful logins, admin URL rotations, and unauthorized admin access attempts were not logged.
**Fix:** Implemented signal receivers for login, added logging to rotation views, and updated middleware to log unauthorized attempts.

## 2. Admin URL Rotation via GET Request [FIXED]
**Description:** The `rotate_admin_url` endpoint was accessible via GET, vulnerable to CSRF.
**Fix:** Converted the view to require POST requests and added CSRF token validation.

## 3. Broad Token Extraction in AdminTokenMiddleware [FIXED]
**Description:** The middleware extracted the admin token from any path segment starting with `admin_`.
**Fix:** Tightened extraction using anchored regex.

## 4. WebCrypto HKDF Misconfiguration [FIXED]
**Description:** In `frontend/crypto.js`, `deriveRootKey` used HKDF improperly for PBKDF2.
**Fix:** Corrected derivation flow to use `deriveBits` first.

## 5. Ineffective AccessGrant Expiration [FIXED]
**Description:** The policy engine checked if an `AccessGrant` was active but ignored the `expires_at` field.
**Fix:** Updated policy to check `expires_at` against `timezone.now()`.

## 6. Subadmin Management Escalation [FIXED]
**Description:** `SUBADMIN` users could manage any non-personal item that had their `department_id` set, even if the scope was `ORG`.
**Fix:** Restricted subadmin management and visibility to only `DEPT` scoped items in their department, unless granted explicitly.
