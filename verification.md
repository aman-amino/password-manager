# Verification (Step 9)

## Security Matrix Checks
- [ ] All endpoints enforce `final-access-matrix.md` rules.
- [ ] Personal secrets remain owner-only, regardless of role.
- [ ] Dept-only secrets accessible only within department for Subadmins.
- [ ] Org-wide secrets accessible only to Admin/Superadmin.
- [ ] Access grants enforced with expiry and audit logging.

## Crypto Validation
- [ ] All encryption/decryption occurs in browser only.
- [ ] PBKDF2 parameters are stored per-user and enforced.
- [ ] AES-256-GCM nonces are random per item.
- [ ] Key wrapping uses ECDH P-256 + AES-GCM.

## Backend Safety
- [ ] DEBUG disabled in production.
- [ ] CSP configured and verified.
- [ ] Axes lockout and rate-limiting enabled.
- [ ] Audit events recorded for access and admin changes.

## UI/Flows
- [ ] Vault list and details load with policy-filtered data.
- [ ] Sharing and revocation flows update access grants.
- [ ] Recovery key setup and usage tested.
