from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.report import ReportFormat, ReportStatus


class ReportRequest(BaseModel):
    institution_id: int
    type: str
    period_label: str
    format: ReportFormat


class ReportResponse(BaseModel):
    id: int
    institution_id: int
    type: str
    period_label: str
    format: ReportFormat
    status: ReportStatus
    file_path: Optional[str]
    narrative: Optional[str]
    generated_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
