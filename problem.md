# Security Findings

## 1. Missing Audit Logs for Security Events [FIXED]
**Fix:** Implemented signal receivers for login and added logging to rotation views/middleware.

## 2. Admin URL Rotation via GET Request [FIXED]
**Fix:** Converted to POST and added CSRF protection.

## 3. Broad Token Extraction in AdminTokenMiddleware [FIXED]
**Fix:** Tightened extraction using anchored regex.

## 4. WebCrypto HKDF Misconfiguration [FIXED]
**Fix:** Corrected derivation flow using `deriveBits`.

## 5. Ineffective AccessGrant Expiration [FIXED]
**Fix:** Added `expires_at` checks in policy engine.

## 6. Subadmin Management Escalation [FIXED]
**Fix:** Restricted subadmin management to `DEPT` scoped items.

## 7. Lack of API Rate Limiting [FIXED]
**Fix:** Configured DRF `AnonRateThrottle` and `UserRateThrottle`.

## 8. Insecure Default Authentication [FIXED]
**Fix:** Disabled `BasicAuthentication` in favor of session-only auth.

## 9. Loose Session Cookie Policy [FIXED]
**Fix:** Set `SESSION_COOKIE_SAMESITE` and `CSRF_COOKIE_SAMESITE` to `Strict`.

## 10. Missing Payload Size Limits [FIXED]
**Fix:** Added 1MB limit to `encrypted_blob` in serializer.
