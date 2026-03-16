"""Simple authentication and authorization utilities."""

from __future__ import annotations

from typing import Dict

from fastapi import Depends, HTTPException, Header, status

# In a real application this data would come from a user database or identity provider
USERS: Dict[str, Dict[str, str]] = {
    # token: {"username": str, "role": str}
    "secret-token": {"username": "alice", "role": "admin"},
    "viewer-token": {"username": "bob", "role": "viewer"},
}


class User:
    """Authenticated user representation."""

    def __init__(self, username: str, role: str, tenant_id: str) -> None:
        self.username = username
        self.role = role
        self.tenant_id = tenant_id


def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
) -> User:
    """Extract and validate the user from the Authorization header and tenant ID."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    user_info = USERS.get(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return User(username=user_info["username"], role=user_info["role"], tenant_id=tenant_id)


def require_role(required_role: str):
    """Dependency generator that checks the user's role."""
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return user

    return dependency