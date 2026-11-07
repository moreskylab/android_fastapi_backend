# backend/app/api/v1/endpoints/tasks.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_repo(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    completed: bool | None = Query(None),
    repo: TaskRepository = Depends(get_task_repo),
) -> list[TaskResponse]:
    tasks = await repo.list_tasks(skip=skip, limit=limit, completed=completed)
    return list(tasks)


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: uuid.UUID,
    repo: TaskRepository = Depends(get_task_repo),
) -> TaskResponse:
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    repo: TaskRepository = Depends(get_task_repo),
) -> TaskResponse:
    return await repo.create(payload)


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    repo: TaskRepository = Depends(get_task_repo),
) -> TaskResponse:
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return await repo.update(task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    repo: TaskRepository = Depends(get_task_repo),
) -> None:
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    await repo.delete(task)