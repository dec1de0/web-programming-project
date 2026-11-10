from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.schemas.common import RequestSchema


class ProjectCreate(RequestSchema):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("Project name cannot be blank")
        return value


class ProjectUpdate(RequestSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def valid_update(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field")
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("Fields cannot be null")
        return self


class ProjectRead(ProjectCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ProjectList(RequestSchema):
    items: list[ProjectRead]
    total: int
    offset: int
    limit: int
