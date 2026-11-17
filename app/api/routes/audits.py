from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status

from app.api.dependencies import get_session
from sqlalchemy.orm import Session
from app.schemas.audits import (
    AuditList,
    AuditRead,
    CodeAuditCreate,
    DesignAuditCreate,
    ReportRead,
)
from app.schemas.common import ErrorResponse
from app.services import audits, findings

router = APIRouter(
    tags=["Audits"],
    responses={404: {"model": ErrorResponse}},
)
DBSession = Annotated[Session, Depends(get_session, scope="function")]


@router.post(
    "/projects/{project_id}/audits",
    response_model=AuditRead,
    status_code=status.HTTP_201_CREATED,
)
def create_audit(
    project_id: UUID,
    data: Annotated[CodeAuditCreate | DesignAuditCreate, Body(discriminator="kind")],
    session: DBSession,
) -> AuditRead:
    return audits.create_audit(session, project_id, data)


@router.get("/projects/{project_id}/audits", response_model=AuditList)
def list_audits(
    project_id: UUID,
    session: DBSession,
    kind: Literal["code", "design"] | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AuditList:
    return audits.list_audits(session, project_id, kind, offset, limit)


@router.get("/audits/{audit_id}", response_model=AuditRead)
def get_audit(audit_id: UUID, session: DBSession) -> AuditRead:
    return audits.get_audit(session, audit_id)


@router.get("/audits/{audit_id}/report", response_model=ReportRead)
def get_report(audit_id: UUID, session: DBSession) -> ReportRead:
    return findings.get_report(session, audit_id)
