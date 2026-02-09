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

## Cryptography Design (Step 2)
- Client-side only: all encryption and decryption happens in the browser via WebCrypto.
- Password KDF: PBKDF2-HMAC-SHA-256 with per-user random salt and high iteration count stored server-side.
- Master key derivation: PBKDF2 output -> root key; subkeys derived with HKDF-SHA-256 for separation.
- Data encryption: AES-256-GCM with per-item random 96-bit nonce.
- Envelope encryption: each secret uses a random 256-bit data key; data key is wrapped by key-encryption keys.
- Key-encryption keys: derived from user root key for personal secrets; org/dept secrets have scope keys.
- Multi-recipient sharing: data key wrapped per authorized recipient using ECDH (P-256) + AES-GCM.
- Integrity: AES-GCM provides confidentiality and integrity; tampering yields authentication failure.
- Key rotation: rotate scope keys periodically; rewrap data keys without re-encrypting ciphertext.
- Recovery: optional recovery key pair stored client-side; server stores only wrapped data keys.
