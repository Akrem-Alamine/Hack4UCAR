from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, func, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    indicator_key: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    operator: Mapped[str] = mapped_column(String(10), nullable=False)  # >, <, >=, <=, ==
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    institution = relationship("Institution", back_populates="alert_rules")
    alerts = relationship("Alert", back_populates="rule")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("alert_rules.id"), nullable=False)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False, index=True)
    indicator_key: Mapped[str] = mapped_column(String(100), nullable=False)
    value_at_trigger: Mapped[float] = mapped_column(Float, nullable=False)
    period_label: Mapped[str] = mapped_column(String(50))
    triggered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    rule = relationship("AlertRule", back_populates="alerts")
    institution = relationship("Institution", back_populates="alerts")
