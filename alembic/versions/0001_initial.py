"""Create projects, audits and findings with integrity constraints."""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_key", sa.String(300), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name_key", name="projects_name_key_key"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_project_name"),
    )
    op.create_table(
        "audits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("rules_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("initial_score", sa.Integer(), nullable=False),
        sa.CheckConstraint("kind IN ('code', 'design')", name="ck_audit_kind"),
        sa.CheckConstraint("initial_score BETWEEN 0 AND 100", name="ck_audit_score"),
    )
    op.create_index("ix_audits_project_id", "audits", ["project_id"])
    op.create_table(
        "findings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "audit_id",
            sa.Uuid(),
            sa.ForeignKey("audits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule_id", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("resolution_note", sa.String(1000)),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_finding_severity",
        ),
        sa.CheckConstraint("status IN ('open', 'resolved')", name="ck_finding_status"),
        sa.CheckConstraint(
            "(status = 'open' AND resolution_note IS NULL) OR (status = 'resolved' AND resolution_note IS NOT NULL AND length(trim(resolution_note)) > 0)",
            name="ck_finding_resolution",
        ),
    )
    op.create_index("ix_findings_audit_id", "findings", ["audit_id"])


def downgrade():
    op.drop_table("findings")
    op.drop_table("audits")
    op.drop_table("projects")
