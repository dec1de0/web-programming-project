from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.errors import ResourceConflict, ResourceNotFound
from app.models import Finding
from app.schemas.audits import ReportRead
from app.schemas.findings import FindingList, FindingRead, FindingUpdate
from app.services.audits import PENALTY, get_audit


def list_findings(session: Session, audit_id: UUID, severity, status, offset, limit):
    get_audit(session, audit_id)
    query = select(Finding).where(Finding.audit_id == audit_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if status:
        query = query.where(Finding.status == status)
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(
        query.order_by(Finding.id).offset(offset).limit(limit)
    ).all()
    return FindingList(
        items=[FindingRead.model_validate(f, from_attributes=True) for f in items],
        total=total,
        offset=offset,
        limit=limit,
    )


def update_finding(
    session: Session, audit_id: UUID, finding_id: UUID, data: FindingUpdate
):
    get_audit(session, audit_id)
    finding = session.scalar(
        select(Finding)
        .where(Finding.id == finding_id, Finding.audit_id == audit_id)
        .with_for_update()
    )
    if finding is None:
        raise ResourceNotFound(
            "Finding not found in this audit", code="finding_not_found"
        )
    if finding.status == data.status:
        raise ResourceConflict(
            "Finding already has this status", code="status_unchanged"
        )
    finding.status = data.status
    finding.resolution_note = (
        data.resolution_note.strip() if data.status == "resolved" else None
    )
    session.flush()
    return finding


def get_report(session: Session, audit_id: UUID):
    audit = get_audit(session, audit_id)
    findings = session.scalars(
        select(Finding).where(Finding.audit_id == audit_id)
    ).all()
    opened = [f for f in findings if f.status == "open"]
    return ReportRead(
        audit_id=audit_id,
        kind=audit.kind,
        initial_score=audit.initial_score,
        current_score=max(0, 100 - sum(PENALTY[f.severity] for f in opened)),
        open_count=len(opened),
        resolved_count=len(findings) - len(opened),
        score_rule="100 minus 5/10/20/30 points per low/medium/high/critical finding",
    )
