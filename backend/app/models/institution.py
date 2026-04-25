from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    acronym: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="institution")
    kpi_records = relationship("KPIRecord", back_populates="institution")
    alert_rules = relationship("AlertRule", back_populates="institution")
    alerts = relationship("Alert", back_populates="institution")
    reports = relationship("Report", back_populates="institution")
    departments = relationship("Department", back_populates="institution")
