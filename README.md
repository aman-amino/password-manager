# Django Password Manager (Zero-Knowledge)

Maximum-security, zero-knowledge password manager with client-side cryptography and strict role-based access.

## Security Goals
- Server never sees plaintext secrets or master keys.
- Personal secrets remain owner-only even for admins.
- Least privilege access aligned with `final-access-matrix.md`.
- Audit logging for all secret operations and role changes.
- Hidden Django admin URL minted on demand by superadmin.

## Threat Model (Summary)
- Assets: encrypted secrets, client master keys, org metadata, audit logs.
- Trust boundaries: browser vs backend API vs database.
- Adversaries: external attackers, malicious insiders, compromised clients.

## Local venv (Windows PowerShell)

```powershell
cd new-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Optional (once you add your backend code here):

```powershell
pip install -r backend\requirements.txt
```

## Docker (dev)

1. Create an env file:

```powershell
copy .env.example .env
```

2. Bring up services:

```powershell
docker compose up -d --build
```

Notes:
- `docker-compose.yml` expects you to create your backend app under `new-manager/backend/`.
- Postgres data persists in the `pgdata` named volume.
