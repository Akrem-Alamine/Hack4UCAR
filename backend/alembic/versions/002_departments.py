"""Add departments and link to kpi_records

Revision ID: 002
Revises: 001
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("domain", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column(
        "kpi_records",
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id"), nullable=True, index=True),
    )


def downgrade():
    op.drop_column("kpi_records", "department_id")
    op.drop_table("departments")
