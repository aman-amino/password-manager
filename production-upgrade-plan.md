# Production Upgrade Plan - Django Password Manager

This document outlines the roadmap for moving this zero-knowledge password manager from a development prototype to a production-grade application.

## 1. Security & Authentication
- [ ] **Full Auth Flow**: Implement user registration with client-side key generation (generating salt, deriving master key, and encrypting the user key).
- [ ] **MFA (TOTP)**: Integrate `django-otp` or a similar library to enforce TOTP for all users, especially admins.
- [ ] **Session Management**: Configure session expiration, concurrent session limits, and secure session cookie settings.
- [ ] **Password Reset**: Implement a zero-knowledge password reset flow using the `RecoveryKey` material already defined in the data model.

## 2. Infrastructure & Deployment
- [ ] **Production Web Server**: Replace `runserver` with `Gunicorn` or `Uvicorn` and use `Nginx` as a reverse proxy.
- [ ] **Database Hardening**: Ensure PostgreSQL is configured with TLS and is not exposed to the public internet.
- [ ] **Docker Hardening**: Use non-root users in Dockerfiles, implement resource limits, and use multi-stage builds to reduce image size.
- [ ] **Secrets Management**: Move all environment variables (DB credentials, Django secret key) to a secure secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault).
- [ ] **HTTPS/TLS**: Enforce TLS 1.3 only and obtain certificates via Let's Encrypt.

## 3. Frontend-Backend Integration
- [ ] **WebCrypto Integration**: Fully integrate `frontend/crypto.js` into the UI for all create/edit/view operations on secrets.
- [ ] **State Management**: Implement a robust frontend state management (e.g., React with Context/Redux) to handle encrypted material in memory securely.
- [ ] **Auto-lock**: Implement a client-side timer to clear sensitive material from memory and log out the user after inactivity.

## 4. Policy & Authorization
- [ ] **Advanced Policy Enforcement**: Refine the policy engine to handle more complex scenarios, such as temporary access grants or department-level admin delegation.
- [ ] **Access Reviews**: Implement a UI for admins to perform periodic access reviews and audits.

## 5. Monitoring & Reliability
- [ ] **Logging & Alerting**: Integrate with a logging service (e.g., ELK stack, Sentry) and set up alerts for suspicious audit events (e.g., multiple failed admin URL attempts).
- [ ] **Backups**: Automate encrypted database backups and test the restoration process regularly.
- [ ] **CI/CD**: Set up a pipeline for automated testing, security scanning (Snyk/Bandit), and zero-downtime deployments.

## 6. Compliance & Auditing
- [ ] **Audit Log Immutability**: Consider using a write-once storage or a blockchain-based log for high-integrity audit events.
- [ ] **Data Retention**: Implement automated cleanup for deleted items and old audit logs according to a defined retention policy.
