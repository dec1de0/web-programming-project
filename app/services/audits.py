from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.errors import ResourceNotFound
from app.models import Audit, Finding
from app.schemas.audits import AuditList, AuditRead, CodeAuditCreate
from app.services.analyzers import Issue, analyze_code, analyze_design
from app.services.projects import get_project

PENALTY = {"low": 5, "medium": 10, "high": 20, "critical": 30}


def score(issues: list[Issue]) -> int:
    return max(0, 100 - sum(PENALTY[issue[3]] for issue in issues))


def get_audit(session: Session, audit_id: UUID):
    audit = session.get(Audit, audit_id)
    if audit is None:
        raise ResourceNotFound("Audit not found", code="audit_not_found")
    return audit


def create_audit(session: Session, project_id: UUID, data):
    # Serialize creation with deletion of the parent project.
    get_project(session, project_id, lock=True)
    issues = (
        analyze_code(data)
        if isinstance(data, CodeAuditCreate)
        else analyze_design(data)
    )
    audit = Audit(project_id=project_id, kind=data.kind, initial_score=score(issues))
    audit.findings = [
        Finding(
            rule_id=rule_id,
            description=description,
            recommendation=recommendation,
            severity=severity,
        )
        for rule_id, description, recommendation, severity in issues
    ]
    session.add(audit)
    session.flush()  # Audit and all findings belong to the same transaction.
    return audit


def list_audits(session: Session, project_id: UUID, kind, offset, limit):
    get_project(session, project_id)
    query = select(Audit).where(Audit.project_id == project_id)
    if kind:
        query = query.where(Audit.kind == kind)
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(
        query.order_by(Audit.created_at, Audit.id).offset(offset).limit(limit)
    ).all()
    return AuditList(
        items=[AuditRead.model_validate(a, from_attributes=True) for a in items],
        total=total,
        offset=offset,
        limit=limit,
    )
