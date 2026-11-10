from uuid import UUID

from app.errors import ResourceConflict, ResourceNotFound
from app.repositories.memory import MemoryStore
from app.schemas.audits import ReportRead
from app.schemas.findings import FindingList, FindingRead, FindingUpdate
from app.services.audits import PENALTY, get_audit


def list_findings(store: MemoryStore, audit_id: UUID, severity: str | None,
                  status: str | None, offset: int, limit: int) -> FindingList:
    with store.lock:
        get_audit(store, audit_id)
        items = [item for item in store.findings.values()
                 if item.audit_id == audit_id
                 and (severity is None or item.severity == severity)
                 and (status is None or item.status == status)]
        return FindingList(items=[item.model_copy(deep=True) for item in items[offset:offset + limit]],
                           total=len(items), offset=offset, limit=limit)


def update_finding(store: MemoryStore, audit_id: UUID, finding_id: UUID,
                   data: FindingUpdate) -> FindingRead:
    with store.lock:
        get_audit(store, audit_id)
        finding = store.findings.get(finding_id)
        if finding is None or finding.audit_id != audit_id:
            raise ResourceNotFound("Finding not found in this audit", code="finding_not_found")
        if finding.status == data.status:
            raise ResourceConflict("Finding already has this status", code="status_unchanged")
        updated = finding.model_copy(update={
            "status": data.status,
            "resolution_note": data.resolution_note.strip() if data.status == "resolved" else None,
        })
        store.findings[finding_id] = updated
        return updated.model_copy(deep=True)


def get_report(store: MemoryStore, audit_id: UUID) -> ReportRead:
    with store.lock:
        audit = get_audit(store, audit_id)
        findings = [item for item in store.findings.values() if item.audit_id == audit_id]
        open_findings = [item for item in findings if item.status == "open"]
        return ReportRead(
            audit_id=audit_id, kind=audit.kind, initial_score=audit.initial_score,
            current_score=max(0, 100 - sum(PENALTY[item.severity] for item in open_findings)),
            open_count=len(open_findings), resolved_count=len(findings) - len(open_findings),
            score_rule="100 minus 5/10/20/30 points per low/medium/high/critical finding",
        )
