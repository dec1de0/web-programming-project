from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_session
from sqlalchemy.orm import Session
from app.schemas.common import ErrorResponse
from app.schemas.findings import (
    FindingList,
    FindingRead,
    FindingStatus,
    FindingUpdate,
    Severity,
)
from app.services import findings

router = APIRouter(
    tags=["Findings"],
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
DBSession = Annotated[Session, Depends(get_session, scope="function")]


@router.get("/audits/{audit_id}/findings", response_model=FindingList)
def list_findings(
    audit_id: UUID,
    session: DBSession,
    severity: Severity | None = None,
    status: FindingStatus | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> FindingList:
    return findings.list_findings(session, audit_id, severity, status, offset, limit)


@router.patch("/audits/{audit_id}/findings/{finding_id}", response_model=FindingRead)
def update_finding(
    audit_id: UUID, finding_id: UUID, data: FindingUpdate, session: DBSession
) -> FindingRead:
    return findings.update_finding(session, audit_id, finding_id, data)
