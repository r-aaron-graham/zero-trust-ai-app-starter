"""FastAPI application demonstrating zero‑trust concepts for an AI service."""

from __future__ import annotations

import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user, require_role, User


class AuditEntry(BaseModel):
    timestamp: datetime.datetime
    user: str
    tenant_id: str
    path: str
    method: str


class AuditLog:
    """In‑memory audit log.  In production this would persist to a database or log service."""

    def __init__(self) -> None:
        self.entries: List[AuditEntry] = []

    def record(self, user: User, path: str, method: str) -> None:
        entry = AuditEntry(
            timestamp=datetime.datetime.utcnow(),
            user=user.username,
            tenant_id=user.tenant_id,
            path=path,
            method=method,
        )
        self.entries.append(entry)


audit_log = AuditLog()

app = FastAPI(title="Zero Trust AI App", version="0.1.0")


@app.middleware("http")
async def audit_middleware(request, call_next):
    """Record audit information for each request that has an authenticated user."""
    response = None
    try:
        # Try to get the current user.  If this fails, we skip audit logging.
        user = get_current_user(
            authorization=request.headers.get("Authorization", ""),
            tenant_id=request.headers.get("X-Tenant-ID", "") or "unknown",
        )
        audit_log.record(user, request.url.path, request.method)
    except HTTPException:
        pass
    response = await call_next(request)
    return response


@app.get("/health")
async def health() -> dict:
    """Public health endpoint."""
    return {"status": "ok"}


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    completion: str


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    req: GenerateRequest,
    user: User = Depends(require_role("admin")),
) -> GenerateResponse:
    """Protected endpoint that echoes the prompt with a prefix.

    In a real application this would call out to an LLM provider.
    """
    # Example: prefix the prompt with the tenant ID to illustrate tenant scoping
    completion = f"Tenant {user.tenant_id}: {req.prompt}"
    return GenerateResponse(completion=completion)


@app.get("/audit")
async def get_audit(user: User = Depends(require_role("admin"))) -> List[AuditEntry]:
    """Return the current audit log entries.  Only admins may view."""
    return [entry for entry in audit_log.entries if entry.tenant_id == user.tenant_id]