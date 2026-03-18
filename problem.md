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
**Description:** Staff users with a valid admin token could access the admin even if they were not superadmins.
**Fix:** Added role-based check in AdminTokenMiddleware.

## 12. Root User in Container [PENDING]
**Description:** Backend container runs as root.
**Priority:** Medium
