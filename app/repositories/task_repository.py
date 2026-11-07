# backend/app/repositories/task_repository.py
import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        completed: bool | None = None,
    ) -> Sequence[TaskModel]:
        stmt = select(TaskModel).order_by(TaskModel.priority.desc(), TaskModel.updated_at.desc())
        if completed is not None:
            stmt = stmt.where(TaskModel.is_completed == completed)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, task_id: uuid.UUID) -> TaskModel | None:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, payload: TaskCreate) -> TaskModel:
        task = TaskModel(**payload.model_dump())
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, task: TaskModel, payload: TaskUpdate) -> TaskModel:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: TaskModel) -> None:
        await self.session.delete(task)
        await self.session.commit()