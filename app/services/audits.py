from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.errors import ResourceNotFound
from app.repositories.memory import MemoryStore
from app.schemas.audits import AuditList, AuditRead, CodeAuditCreate, DesignAuditCreate
from app.schemas.findings import FindingRead
from app.services.analyzers import Issue, analyze_code, analyze_design
from app.services.projects import get_project

PENALTY = {"low": 5, "medium": 10, "high": 20, "critical": 30}


def score(issues: list[Issue]) -> int:
    return max(0, 100 - sum(PENALTY[issue[3]] for issue in issues))


def get_audit(store: MemoryStore, audit_id: UUID) -> AuditRead:
    with store.lock:
        audit = store.audits.get(audit_id)
        if audit is None:
            raise ResourceNotFound("Audit not found", code="audit_not_found")
        return audit.model_copy(deep=True)


def create_audit(store: MemoryStore, project_id: UUID,
                 data: CodeAuditCreate | DesignAuditCreate) -> AuditRead:
    with store.lock:
        get_project(store, project_id)
        issues = analyze_code(data) if isinstance(data, CodeAuditCreate) else analyze_design(data)
        audit = AuditRead(id=uuid4(), project_id=project_id, kind=data.kind,
                          rules_version="1", created_at=datetime.now(timezone.utc),
                          initial_score=score(issues))
        findings = [
            FindingRead(id=uuid4(), audit_id=audit.id, rule_id=rule_id,
                        description=description, recommendation=recommendation, severity=severity)
            for rule_id, description, recommendation, severity in issues
        ]
        store.audits[audit.id] = audit
        for finding in findings:
            store.findings[finding.id] = finding
        return audit.model_copy(deep=True)


def list_audits(store: MemoryStore, project_id: UUID, kind: str | None,
                offset: int, limit: int) -> AuditList:
    with store.lock:
        get_project(store, project_id)
        items = [item for item in store.audits.values()
                 if item.project_id == project_id and (kind is None or item.kind == kind)]
        items.sort(key=lambda item: item.created_at)
        return AuditList(items=[item.model_copy(deep=True) for item in items[offset:offset + limit]],
                         total=len(items), offset=offset, limit=limit)
