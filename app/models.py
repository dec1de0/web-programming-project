"""Persistent domain models. Schema changes are applied through Alembic."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_project_name"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    name_key: Mapped[str] = mapped_column(String(300), unique=True)
    description: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, onupdate=now
    )
    audits: Mapped[list["Audit"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", passive_deletes=True
    )


class Audit(Base):
    __tablename__ = "audits"
    __table_args__ = (
        CheckConstraint("kind IN ('code', 'design')", name="ck_audit_kind"),
        CheckConstraint("initial_score BETWEEN 0 AND 100", name="ck_audit_score"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(10))
    rules_version: Mapped[str] = mapped_column(String(20), default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    initial_score: Mapped[int] = mapped_column(Integer)
    project: Mapped[Project] = relationship(back_populates="audits")
    findings: Mapped[list["Finding"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan", passive_deletes=True
    )


class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_finding_severity",
        ),
        CheckConstraint("status IN ('open', 'resolved')", name="ck_finding_status"),
        CheckConstraint(
            "(status = 'open' AND resolution_note IS NULL) OR (status = 'resolved' AND resolution_note IS NOT NULL AND length(trim(resolution_note)) > 0)",
            name="ck_finding_resolution",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    audit_id: Mapped[UUID] = mapped_column(
        ForeignKey("audits.id", ondelete="CASCADE"), index=True
    )
    rule_id: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(10), default="open")
    resolution_note: Mapped[str | None] = mapped_column(String(1000))
    audit: Mapped[Audit] = relationship(back_populates="findings")
