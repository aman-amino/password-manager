# Hardening Checklist (Step 8)

- [ ] Enforce HTTPS-only (HSTS, SECURE_SSL_REDIRECT) in production.
- [ ] Configure CSP for frontend and admin to allow only trusted origins.
- [ ] Disable DEBUG in production and set explicit ALLOWED_HOSTS.
- [ ] Rotate Django SECRET_KEY and store only in environment variables.
- [ ] Enable secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE).
- [ ] Set SESSION_COOKIE_HTTPONLY and CSRF_COOKIE_HTTPONLY where applicable.
- [ ] Use secure password validators and minimum length policy.
- [ ] Configure rate limiting / Axes with alerting and lockout policies.
- [ ] Ensure database connections use TLS.
- [ ] Enforce least-privilege DB credentials.
- [ ] Audit log all secret reads/writes and admin actions.
- [ ] Encrypt backups and set retention policies.
- [ ] Disable unused endpoints and admin access for non-superadmins.
- [ ] Set Django admin URL rotation and audit each access.
- [ ] Verify all API endpoints enforce object-level permissions.
- [ ] Run dependency and container image vulnerability scans.
- [ ] Maintain SRI hashes for CDN assets or self-host critical assets.
