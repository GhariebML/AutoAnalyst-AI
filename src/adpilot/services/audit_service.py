"""Audit logging service."""

from __future__ import annotations

import json
from uuid import uuid4
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.audit_log import AuditLog


async def log_action(
    session: AsyncSession,
    user_id: str | None,
    organization_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> AuditLog:
    """Record an action to the audit logs database table."""
    payload_json = json.dumps(payload) if payload else None
    log_entry = AuditLog(
        id=f"audit-{uuid4().hex[:12]}",
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=payload_json,
    )
    session.add(log_entry)
    return log_entry
