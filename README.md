# Zero‑Trust AI App Starter

This repository provides a minimal template for building AI applications with zero‑trust
principles.  Zero‑trust means that **every request is authenticated and authorized**, secrets
are managed securely, audit logs are recorded, and tenant boundaries are enforced.  This
starter uses FastAPI and simple middleware to illustrate these concepts without pulling in
heavy dependencies.

## Features

* **Authentication** – Basic token‑based authentication with per‑user roles.
* **Authorization** – Dependency functions enforce role‑based access control on endpoints.
* **Tenant isolation** – Each request is associated with a tenant ID; data is scoped to the
  tenant.
* **Audit logging** – Middleware records request metadata and stores logs in memory for review.
* **Demo credentials** – The example tokens are fixed fixtures for local use.

## Usage

Install dependencies and run the app:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

The app defines two endpoints:

* `GET /health` – Public health check.
* `POST /generate` – Protected endpoint that accepts a prompt and returns a dummy completion.
  Requires an API token and appropriate role.  The request must also include a tenant ID in
  the headers.

### Example request

```bash
curl -X POST http://localhost:8000/generate \
     -H "Authorization: Bearer secret-token" \
     -H "X-Tenant-ID: tenant1" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain zero trust"}'
```

Changing the example tenant header to `tenant2` returns HTTP 403.
The admin audit endpoint returns entries for the authenticated tenant.

## Extending

This starter is not production‑ready.  In a real system you would integrate with a
centralized identity provider, use a secrets manager (e.g. Vault or AWS Secrets Manager),
persist audit logs to a database, and implement multi‑tenant data isolation at the database
layer.  Use this template as a reference for structuring such a system.