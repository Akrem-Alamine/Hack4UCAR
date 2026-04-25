from pydantic import BaseModel
from datetime import datetime


class InstitutionBase(BaseModel):
    name: str
    acronym: str
    type: str
    city: str


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionResponse(InstitutionBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InstitutionSummary(BaseModel):
    id: int
    name: str
    acronym: str
    city: str

    model_config = {"from_attributes": True}
