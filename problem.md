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
## 16. Superadmin Inconsistent Visibility [FIXED]
## 17. Weak Default Password Policy [FIXED]

## 18. MFA Definition without Enforcement [FIXED]
**Description:** The `User` model had an `mfa_enabled` flag, but the authentication logic did not enforce it.
**Fix:** Implemented `MFAEnforcementMiddleware` that blocks all non-exempt paths if a user has MFA enabled but has not verified it in their current session (`mfa_verified` session key).
