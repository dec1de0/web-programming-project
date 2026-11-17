from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import Project
from app.errors import ResourceNotFound
from app.schemas.projects import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate


def get_project(session: Session, project_id: UUID, *, lock=False):
    query = select(Project).where(Project.id == project_id)
    if lock:
        query = query.with_for_update()
    project = session.scalar(query)
    if project is None:
        raise ResourceNotFound("Project not found", code="project_not_found")
    return project


def list_projects(session: Session, search, offset, limit):
    query = select(Project)
    if search:
        query = query.where(
            Project.name_key.contains(search.casefold(), autoescape=True)
        )
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(
        query.order_by(Project.created_at, Project.id).offset(offset).limit(limit)
    ).all()
    return ProjectList(
        items=[ProjectRead.model_validate(p, from_attributes=True) for p in items],
        total=total,
        offset=offset,
        limit=limit,
    )


def create_project(session: Session, data: ProjectCreate):
    project = Project(**data.model_dump(), name_key=data.name.casefold())
    session.add(project)
    session.flush()
    return project


def update_project(session: Session, project_id: UUID, data: ProjectUpdate):
    project = get_project(session, project_id, lock=True)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.name_key = project.name.casefold()
    session.flush()
    return project


def delete_project(session: Session, project_id: UUID):
    session.delete(get_project(session, project_id, lock=True))
    session.flush()
