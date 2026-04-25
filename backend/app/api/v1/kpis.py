from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.kpi import KPIRecord
from app.schemas.kpi import KPIRecordCreate, KPIRecordResponse
from app.dependencies.auth import get_current_user, get_scoped_institution_id
from app.services.kpi_service import get_latest_kpis, get_kpi_trend, get_cross_institution_comparison

router = APIRouter(prefix="/kpis", tags=["KPIs"])


def _effective_domain(user: User, requested_domain: Optional[str]) -> Optional[str]:
    """Department users are locked to their domain regardless of what's requested."""
    if user.domain_scope:
        return user.domain_scope
    return requested_domain


@router.get("/", response_model=list[dict])
def list_kpis(
    institution_id: Optional[int] = Query(None),
    domain: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    effective = _effective_domain(current_user, domain)
    return get_latest_kpis(db, scoped_id, effective)


@router.get("/trend", response_model=dict)
def kpi_trend(
    institution_id: int = Query(...),
    indicator_key: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    return get_kpi_trend(db, scoped_id, indicator_key)


@router.get("/compare", response_model=list[dict])
def compare_institutions(
    indicator_key: str = Query(...),
    period_label: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value != "super_admin":
        raise HTTPException(status_code=403, detail="Réservé aux super administrateurs")
    return get_cross_institution_comparison(db, indicator_key, period_label)


@router.get("/periods", response_model=list[str])
def list_periods(
    institution_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    query = db.query(KPIRecord.period_label).distinct()
    if scoped_id:
        query = query.filter(KPIRecord.institution_id == scoped_id)
    rows = query.order_by(KPIRecord.period_label).all()
    return [r[0] for r in rows]


@router.post("/", response_model=KPIRecordResponse)
def create_kpi_record(
    payload: KPIRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.domain_scope and payload.domain != current_user.domain_scope:
        raise HTTPException(status_code=403, detail=f"Votre compte est limité au domaine '{current_user.domain_scope}'")
    record = KPIRecord(**payload.model_dump(), created_by=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
