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
**Description:** Backend container was running as root.
**Fix:** Created 'vault' user and group in Dockerfile.

## 13. Superadmin Management Restriction [FIXED]
**Description:** Superadmins were restricted from managing items outside their own organization even though they could see them.
**Fix:** Unified management logic in policy engine.
