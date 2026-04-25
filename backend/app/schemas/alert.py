from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.alert import AlertSeverity


class AlertRuleCreate(BaseModel):
    institution_id: Optional[int] = None
    name: str
    indicator_key: str
    domain: str
    operator: str
    threshold: float
    severity: AlertSeverity
    description: Optional[str] = None


class AlertRuleResponse(BaseModel):
    id: int
    institution_id: Optional[int]
    name: str
    indicator_key: str
    domain: str
    operator: str
    threshold: float
    severity: AlertSeverity
    description: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: int
    rule_id: int
    institution_id: int
    institution_name: Optional[str] = None
    indicator_key: str
    value_at_trigger: float
    period_label: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    is_resolved: bool
    severity: Optional[AlertSeverity] = None
    explanation: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    alert_id: int
