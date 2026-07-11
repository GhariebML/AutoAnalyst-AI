"""Repository for managing CampaignTask persistence."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from sqlalchemy import select

from ..core.database import async_session_factory
from ..models.campaign_task import CampaignTask


class CampaignRepository:
    """Handles CRUD operations for CampaignTask models."""

    async def create_task(self, task_id: str, brief_json: Optional[str] = None) -> CampaignTask:
        """Create a new pending campaign task."""
        async with async_session_factory() as session:
            task = CampaignTask(task_id=task_id, status="pending", progress=0, brief_json=brief_json)
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def update_task(
        self,
        task_id: str,
        status: str,
        progress: int,
        message: Optional[str] = None,
    ) -> Optional[CampaignTask]:
        """Update task progress and status."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = status
                task.progress = progress
                if message is not None:
                    task.message = message
                await session.commit()
                await session.refresh(task)
            return task

    async def set_content(self, task_id: str, content: Dict[str, Any]) -> None:
        """Store completed campaign content as JSON."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.content_json = json.dumps(content)
                task.status = "completed"
                task.progress = 100
                task.message = "Campaign package ready"
                await session.commit()

    async def set_error(self, task_id: str, error_message: str) -> None:
        """Store an error for a failed task."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.progress = 100
                task.error_message = error_message
                task.message = "Campaign generation failed"
                await session.commit()

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Return task status as a dict compatible with TaskResponse, or None."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task is None:
                return None
            return {
                "taskId": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "message": task.message,
            }

    async def get_content(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Return stored content dict, or None."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task is None or task.content_json is None:
                return None
            return json.loads(task.content_json)

    async def get_error(self, task_id: str) -> Optional[str]:
        """Return stored error message, or None."""
        async with async_session_factory() as session:
            result = await session.execute(select(CampaignTask).where(CampaignTask.task_id == task_id))
            task = result.scalar_one_or_none()
            if task is None:
                return None
            return task.error_message
