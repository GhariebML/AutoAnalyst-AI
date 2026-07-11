"""API key and user session token authentication dependencies."""

from __future__ import annotations

from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from ..core.config import get_config
from ..core.database import async_session_factory
from ..models.user import User

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_security = HTTPBearer(auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(_api_key_header),
) -> None:
    """Validate the ``X-API-Key`` header against the configured key.

    When ``ADPILOT_API_KEY`` is empty (development mode), authentication is
    skipped so the dashboard and scripts work without extra setup.
    """
    configured_key = get_config().api_key
    if not configured_key:
        return  # Dev mode — no key configured, skip auth
    if api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_security),
) -> User:
    """Retrieve the current authenticated user via Bearer token (user_id)."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )
    
    token = credentials.credentials
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == token))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token or user not found",
            )
        return user


def require_role(allowed_roles: List[str]) -> Callable:
    """Enforce that the current user has one of the allowed roles."""
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of the following roles: {', '.join(allowed_roles)}",
            )
        return user
    return dependency
