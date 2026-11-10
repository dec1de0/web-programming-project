from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_store
from app.repositories.memory import MemoryStore
from app.schemas.common import ErrorResponse
from app.schemas.findings import (
    FindingList, FindingRead, FindingStatus, FindingUpdate, Severity,
)
from app.services import findings

router = APIRouter(
    tags=["Findings"], responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
Store = Annotated[MemoryStore, Depends(get_store)]


@router.get("/audits/{audit_id}/findings", response_model=FindingList)
def list_findings(audit_id: UUID, store: Store,
                  severity: Severity | None = None, status: FindingStatus | None = None,
                  offset: Annotated[int, Query(ge=0)] = 0,
                  limit: Annotated[int, Query(ge=1, le=100)] = 20) -> FindingList:
    return findings.list_findings(store, audit_id, severity, status, offset, limit)


@router.patch("/audits/{audit_id}/findings/{finding_id}", response_model=FindingRead)
def update_finding(audit_id: UUID, finding_id: UUID, data: FindingUpdate,
                   store: Store) -> FindingRead:
    return findings.update_finding(store, audit_id, finding_id, data)
