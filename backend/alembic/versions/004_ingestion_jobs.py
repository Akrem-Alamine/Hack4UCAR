"""004 ingestion jobs

Revision ID: 004
Revises: 003
Create Date: 2025-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types only if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobstatus AS ENUM ('pending', 'processing', 'completed', 'failed');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobsourcetype AS ENUM ('pdf', 'image', 'excel', 'csv');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create the table only if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_jobs (
            id SERIAL PRIMARY KEY,
            institution_id INTEGER NOT NULL REFERENCES institutions(id),
            created_by INTEGER NOT NULL REFERENCES users(id),
            source_type jobsourcetype NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            status jobstatus NOT NULL DEFAULT 'pending',
            error_message TEXT,
            extracted_text TEXT,
            extracted_kpis JSONB,
            kpi_count INTEGER DEFAULT 0,
            quality_score INTEGER DEFAULT 0,
            imported_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            completed_at TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_ingestion_jobs_status ON ingestion_jobs (status);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ingestion_jobs_institution_id ON ingestion_jobs (institution_id);")


def downgrade():
    op.drop_table("ingestion_jobs")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS jobsourcetype")
