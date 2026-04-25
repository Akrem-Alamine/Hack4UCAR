"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("acronym", sa.String(20), nullable=False, unique=True),
        sa.Column("type", sa.String(100)),
        sa.Column("city", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("role", sa.Enum("super_admin", "president", "dean", "staff", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "kpi_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False, index=True),
        sa.Column("domain", sa.String(50), nullable=False, index=True),
        sa.Column("indicator_key", sa.String(100), nullable=False, index=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(30)),
        sa.Column("period_label", sa.String(50), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("indicator_key", sa.String(100), nullable=False),
        sa.Column("domain", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(10), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.Enum("info", "warning", "critical", name="alertseverity"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("alert_rules.id"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False, index=True),
        sa.Column("indicator_key", sa.String(100), nullable=False),
        sa.Column("value_at_trigger", sa.Float(), nullable=False),
        sa.Column("period_label", sa.String(50)),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), server_default="false"),
        sa.Column("explanation", sa.Text(), nullable=True),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False, index=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("period_label", sa.String(50), nullable=False),
        sa.Column("format", sa.Enum("pdf", "excel", name="reportformat"), nullable=False),
        sa.Column("status", sa.Enum("pending", "generating", "ready", "failed", name="reportstatus"), server_default="pending"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("generated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("reports")
    op.drop_table("alerts")
    op.drop_table("alert_rules")
    op.drop_table("kpi_records")
    op.drop_table("users")
    op.drop_table("institutions")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS reportformat")
    op.execute("DROP TYPE IF EXISTS reportstatus")
