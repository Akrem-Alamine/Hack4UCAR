from sqlalchemy import String, DateTime, ForeignKey, func, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class ReportFormat(str, enum.Enum):
    pdf = "pdf"
    excel = "excel"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    generating = "generating"
    ready = "ready"
    failed = "failed"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)
    format: Mapped[ReportFormat] = mapped_column(Enum(ReportFormat), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.pending)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    institution = relationship("Institution", back_populates="reports")
