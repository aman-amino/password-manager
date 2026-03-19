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

## 19. Missing Logout Audit Logging [FIXED]
**Description:** User logouts were not being captured in the audit trail.
**Fix:** Added a signal receiver for `user_logged_out` in `vault/signals.py`.

## 20. Excessive Session Lifetime [FIXED]
**Description:** Default Django session age (2 weeks) was too long for a sensitive application.
**Fix:** Reduced `SESSION_COOKIE_AGE` to 1 hour and enabled `SESSION_EXPIRE_AT_BROWSER_CLOSE`.
