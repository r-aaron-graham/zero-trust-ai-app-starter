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

## Verify tenant scope

```bash
python -m pip install -r requirements.txt httpx
python -m unittest discover -s tests -v
```

The tests exercise allowed generation, a mismatched tenant header, and
audit filtering. GitHub Actions runs the same checks.

## Extending

This starter is not production‑ready.  In a real system you would integrate with a
centralized identity provider, use a secrets manager (e.g. Vault or AWS Secrets Manager),
persist audit logs to a database, and implement multi‑tenant data isolation at the database
layer.  Use this template as a reference for structuring such a system.

## Deployment verification

Build the reviewer container from the repository root.

```sh
docker build -t reviewer-smoke .
docker run --rm -p 127.0.0.1:8000:8000 reviewer-smoke
```

From another terminal, run `curl --fail http://127.0.0.1:8000/health`. Expect HTTP 200. Stop the container with Ctrl+C when finished. The bundled identities and tokens are fixtures. Replace them with trusted identity verification and provision tenant-specific access before any shared deployment.

## Reproduce the CI dependency set

Use Python 3.12 on Linux. GitHub Actions and the Docker build apply `requirements.lock` as pip constraints. The file pins resolved runtime and test dependencies. For a local install, add `-c requirements.lock` to the install command above. Verify the installed packages with `python -m pip check`.

When updating dependencies, resolve the runtime and test requirements together in a clean Python 3.12 environment and rerun CI, including the container smoke test.
