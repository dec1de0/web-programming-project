from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_session
from sqlalchemy.orm import Session
from app.schemas.common import ErrorResponse
from app.schemas.projects import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate
from app.services import projects

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
DBSession = Annotated[Session, Depends(get_session, scope="function")]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, session: DBSession) -> ProjectRead:
    return projects.create_project(session, data)


@router.get("", response_model=ProjectList)
def list_projects(
    session: DBSession,
    search: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProjectList:
    return projects.list_projects(session, search, offset, limit)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, session: DBSession) -> ProjectRead:
    return projects.get_project(session, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID, data: ProjectUpdate, session: DBSession
) -> ProjectRead:
    return projects.update_project(session, project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, session: DBSession) -> Response:
    projects.delete_project(session, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
