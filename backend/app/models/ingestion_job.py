import enum
from datetime import datetime
from sqlalchemy import Integer, String, Enum, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobSourceType(str, enum.Enum):
    pdf = "pdf"
    image = "image"
    excel = "excel"
    csv = "csv"


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institution_id: Mapped[int] = mapped_column(Integer, ForeignKey("institutions.id"), index=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    source_type: Mapped[JobSourceType] = mapped_column(Enum(JobSourceType))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.pending, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Raw extracted text (from OCR or Excel)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structured KPIs extracted by AI
    extracted_kpis: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Quality metrics
    kpi_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[int] = mapped_column(Integer, default=0)
    imported_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
