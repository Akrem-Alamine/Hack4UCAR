from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class KPIRecordCreate(BaseModel):
    institution_id: int
    domain: str
    indicator_key: str
    value: float
    unit: str
    period_label: str
    period_start: date
    period_end: date
    notes: Optional[str] = None


class KPIRecordResponse(BaseModel):
    id: int
    institution_id: int
    domain: str
    indicator_key: str
    value: float
    unit: str
    period_label: str
    period_start: date
    period_end: date
    recorded_at: datetime

    model_config = {"from_attributes": True}


class KPIAggregation(BaseModel):
    institution_id: int
    institution_name: str
    institution_acronym: str
    domain: str
    indicator_key: str
    value: float
    unit: str
    period_label: str
    trend: Optional[str] = None
    is_anomaly: Optional[bool] = False
    z_score: Optional[float] = None


class KPIForecast(BaseModel):
    institution_id: int
    indicator_key: str
    historical_values: list[float]
    historical_labels: list[str]
    forecast_values: list[float]
    forecast_labels: list[str]
    trend: str
    slope: float


class DomainSummary(BaseModel):
    domain: str
    indicators: list[KPIAggregation]
