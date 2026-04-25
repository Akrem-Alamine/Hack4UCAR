"""Add domain_scope to users and update role enum

Revision ID: 003
Revises: 002
Create Date: 2026-04-25
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("domain_scope", sa.String(50), nullable=True))

    # Add 'department' to the userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'department'")


def downgrade():
    op.drop_column("users", "domain_scope")
