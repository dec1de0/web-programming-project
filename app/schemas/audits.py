from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import RequestSchema


class CodeAuditCreate(RequestSchema):
    kind: Literal["code"]
    source: str = Field(min_length=1, max_length=50000)


class DesignElement(RequestSchema):
    kind: Literal["text", "button", "input", "link"]
    label: str | None = Field(default=None, max_length=200)
    text_color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    background_color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    font_size: int = Field(gt=0, le=200)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)


class DesignAuditCreate(RequestSchema):
    kind: Literal["design"]
    elements: list[DesignElement] = Field(min_length=1, max_length=100)


AuditCreate = Annotated[CodeAuditCreate | DesignAuditCreate, Field(discriminator="kind")]


class AuditRead(RequestSchema):
    id: UUID
    project_id: UUID
    kind: Literal["code", "design"]
    rules_version: str
    created_at: datetime
    initial_score: int = Field(ge=0, le=100)


class AuditList(RequestSchema):
    items: list[AuditRead]
    total: int
    offset: int
    limit: int


class ReportRead(RequestSchema):
    audit_id: UUID
    kind: Literal["code", "design"]
    initial_score: int
    current_score: int
    open_count: int
    resolved_count: int
    score_rule: str
