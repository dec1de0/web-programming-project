"""One in-memory store per FastAPI application instance."""

from threading import RLock
from uuid import UUID

from app.schemas.audits import AuditRead
from app.schemas.findings import FindingRead
from app.schemas.projects import ProjectRead


class MemoryStore:
    def __init__(self) -> None:
        self.projects: dict[UUID, ProjectRead] = {}
        self.audits: dict[UUID, AuditRead] = {}
        self.findings: dict[UUID, FindingRead] = {}
        self.lock = RLock()
