from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_store
from app.repositories.memory import MemoryStore
from app.schemas.common import ErrorResponse
from app.schemas.projects import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate
from app.services import projects

router = APIRouter(
    prefix="/projects", tags=["Projects"],
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
Store = Annotated[MemoryStore, Depends(get_store)]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, store: Store) -> ProjectRead:
    return projects.create_project(store, data)


@router.get("", response_model=ProjectList)
def list_projects(store: Store, search: str | None = None,
                  offset: Annotated[int, Query(ge=0)] = 0,
                  limit: Annotated[int, Query(ge=1, le=100)] = 20) -> ProjectList:
    return projects.list_projects(store, search, offset, limit)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, store: Store) -> ProjectRead:
    return projects.get_project(store, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: UUID, data: ProjectUpdate, store: Store) -> ProjectRead:
    return projects.update_project(store, project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, store: Store) -> Response:
    projects.delete_project(store, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
