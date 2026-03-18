# Security Findings

## 1. Missing Audit Logs for Security Events [FIXED]
**Description:** Successful logins, admin URL rotations, and unauthorized admin access attempts were not logged in the AuditEvent table.
**Fix:** Implemented signal receivers for login, added logging to rotation views, and updated middleware to log unauthorized attempts.

## 2. Admin URL Rotation via GET Request [FIXED]
**Description:** The `rotate_admin_url` endpoint was accessible via GET, vulnerable to CSRF.
**Fix:** Converted the view to require POST requests and added CSRF token validation in the frontend.

## 3. Broad Token Extraction in AdminTokenMiddleware [FIXED]
**Description:** The middleware extracted the admin token from any path segment starting with `admin_`.
**Fix:** Tightened the extraction using a strict regex anchored to the start of the path.

## 4. WebCrypto HKDF Misconfiguration [FIXED]
**Description:** In `frontend/crypto.js`, `deriveRootKey` used HKDF as the target key type for PBKDF2 derivation improperly.
**Fix:** Corrected the derivation flow to use `deriveBits` for the root material and then `importKey` for the HKDF base.

## 5. Ineffective AccessGrant Expiration [PENDING]
**Description:** The policy engine checks if an `AccessGrant` is active but ignores the `expires_at` field.
**Impact:** Users can retain access to items indefinitely even after their grant has supposedly expired.
**Priority:** High

## 6. Subadmin Management Escalation [PENDING]
**Description:** `SUBADMIN` users can manage any non-personal item that has their `department_id` set, regardless of whether the scope is `DEPT` or `ORG`.
**Impact:** Subadmins could potentially modify organization-wide items if they were created within their department.
**Priority:** Medium
