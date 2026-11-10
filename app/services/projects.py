from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.errors import ResourceConflict, ResourceNotFound
from app.repositories.memory import MemoryStore
from app.schemas.projects import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate


def get_project(store: MemoryStore, project_id: UUID) -> ProjectRead:
    with store.lock:
        project = store.projects.get(project_id)
        if project is None:
            raise ResourceNotFound("Project not found", code="project_not_found")
        return project.model_copy(deep=True)


def list_projects(store: MemoryStore, search: str | None, offset: int, limit: int) -> ProjectList:
    with store.lock:
        items = list(store.projects.values())
        if search:
            items = [item for item in items if search.casefold() in item.name.casefold()]
        items.sort(key=lambda item: item.created_at)
        return ProjectList(
            items=[item.model_copy(deep=True) for item in items[offset:offset + limit]],
            total=len(items), offset=offset, limit=limit,
        )


def create_project(store: MemoryStore, data: ProjectCreate) -> ProjectRead:
    with store.lock:
        if any(item.name.casefold() == data.name.casefold() for item in store.projects.values()):
            raise ResourceConflict("Project name already exists", code="project_name_taken")
        now = datetime.now(timezone.utc)
        project = ProjectRead(id=uuid4(), name=data.name, description=data.description,
                              created_at=now, updated_at=now)
        store.projects[project.id] = project
        return project.model_copy(deep=True)


def update_project(store: MemoryStore, project_id: UUID, data: ProjectUpdate) -> ProjectRead:
    with store.lock:
        project = get_project(store, project_id)
        values = data.model_dump(exclude_unset=True)
        name = values.get("name", project.name)
        if any(item.id != project_id and item.name.casefold() == name.casefold()
               for item in store.projects.values()):
            raise ResourceConflict("Project name already exists", code="project_name_taken")
        updated = project.model_copy(update={**values, "updated_at": datetime.now(timezone.utc)})
        store.projects[project_id] = updated
        return updated.model_copy(deep=True)


def delete_project(store: MemoryStore, project_id: UUID) -> None:
    with store.lock:
        get_project(store, project_id)
        audit_ids = {item.id for item in store.audits.values() if item.project_id == project_id}
        for finding_id, finding in list(store.findings.items()):
            if finding.audit_id in audit_ids:
                del store.findings[finding_id]
        for audit_id in audit_ids:
            del store.audits[audit_id]
        del store.projects[project_id]
