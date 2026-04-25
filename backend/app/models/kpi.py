from sqlalchemy import String, Float, DateTime, ForeignKey, Date, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class KPIRecord(Base):
    __tablename__ = "kpi_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False, index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    indicator_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(30))
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    institution = relationship("Institution", back_populates="kpi_records")
    department = relationship("Department", back_populates="kpi_records")
