from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import RequestSchema

Severity = Literal["low", "medium", "high", "critical"]
FindingStatus = Literal["open", "resolved"]


class FindingRead(RequestSchema):
    id: UUID
    audit_id: UUID
    rule_id: str
    description: str
    recommendation: str
    severity: Severity
    status: FindingStatus = "open"
    resolution_note: str | None = None


class FindingUpdate(RequestSchema):
    status: FindingStatus
    resolution_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def note_for_resolution(self):
        if self.status == "resolved" and not (self.resolution_note or "").strip():
            raise ValueError("A resolution note is required when resolving a finding")
        if self.status == "open" and self.resolution_note is not None:
            raise ValueError("Do not send a resolution note when reopening a finding")
        return self


class FindingList(RequestSchema):
    items: list[FindingRead]
    total: int
    offset: int
    limit: int
