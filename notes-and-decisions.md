# Notes And Decisions

## Threat Model (Step 1)
- Primary assets: encrypted secrets, client master keys, org metadata, audit logs.
- Trust boundaries: browser vs backend API vs database.
- Adversaries: external attackers, malicious insiders, compromised clients, credential stuffing.
- Key assumptions: TLS enforced; browsers provide WebCrypto; users protect devices.

## Security Goals
- Zero-knowledge: server never learns plaintext secrets or master keys.
- Integrity: tamper-evident storage and audit logging for all secret operations.
- Least privilege: role-based access aligned with final-access-matrix.md.
- Admin minimization: hidden admin URL generated on demand by superadmin only.
- Secure defaults: deny by default, explicit access grants, rate limiting.

## Open Questions
- Policy engine representation for department scoping and owner-only secrets.
- How to handle emergency recovery without breaking zero-knowledge guarantees.

## Environment Notes
- Pinned backend dependencies to latest versions on 2026-02-09 in `backend/requirements.txt`.
- `python -m venv .venv` succeeded, but `ensurepip` failed due to temp folder permission errors.
- Rechecked package versions on 2026-02-09; Gunicorn pinned to `25.0.3`.
