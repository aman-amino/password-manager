# Security Findings

## 1. Missing Audit Logs for Security Events [FIXED]
## 2. Admin URL Rotation via GET Request [FIXED]
## 3. Broad Token Extraction in AdminTokenMiddleware [FIXED]
## 4. WebCrypto HKDF Misconfiguration [FIXED]
## 5. Ineffective AccessGrant Expiration [FIXED]
## 6. Subadmin Management Escalation [FIXED]
## 7. Lack of API Rate Limiting [FIXED]
## 8. Insecure Default Authentication [FIXED]
## 9. Loose Session Cookie Policy [FIXED]
## 10. Missing Payload Size Limits [FIXED]
## 11. Admin Access Bypass by Non-Superadmin Staff [FIXED]
## 12. Root User in Container [FIXED]
## 13. Superadmin Management Restriction [FIXED]
## 14. Unaudited Django Admin Actions [FIXED]

## 15. Sensitive Token Exposure in Logs [FIXED]
**Description:** The secret admin token was being logged in the `AuditEvent` metadata path field.
**Fix:** Implemented token redaction in `AdminTokenMiddleware`.

## 16. Superadmin Inconsistent Visibility [FIXED]
**Description:** Superadmins were unable to see other users' personal items in the list view even when granted explicit access.
**Fix:** Updated queryset filtering for superadmins.

## 17. MFA Definition without Enforcement [PENDING]
**Description:** The `User` model has an `mfa_enabled` flag, but the authentication logic does not enforce or provide MFA.
**Priority:** High

## 18. Weak Default Password Policy [PENDING]
**Description:** Default Django validators may be too lenient for a secure vault.
**Priority:** Medium
