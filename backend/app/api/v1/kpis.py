from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.kpi import KPIRecord
from app.schemas.kpi import KPIRecordCreate, KPIRecordResponse
from app.dependencies.auth import get_current_user, get_scoped_institution_id
from app.services.kpi_service import get_latest_kpis, get_kpi_trend, get_cross_institution_comparison
from app.services.ranking_service import get_institutions_ranking, compute_institution_health
from app.ai.insights import generate_domain_insights
from app.models.institution import Institution

router = APIRouter(prefix="/kpis", tags=["KPIs"])

DOMAIN_LABELS = {
    "academic": "Académique", "finance": "Finance", "hr": "Ressources Humaines",
    "esg": "ESG / RSE", "insertion": "Insertion Professionnelle", "research": "Recherche",
    "infrastructure": "Infrastructure", "partnerships": "Partenariats",
    "student_life": "Vie Estudiantine",
}


def _effective_domain(user: User, requested_domain: Optional[str]) -> Optional[str]:
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
    if current_user.role.value not in ("super_admin", "president"):
        raise HTTPException(status_code=403, detail="Accès insuffisant")
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


# ─── Track 2: Ranking & Health Index ─────────────────────────────────────────

@router.get("/ranking")
def institutions_ranking(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value not in ("super_admin", "president"):
        raise HTTPException(status_code=403, detail="Accès insuffisant")
    return get_institutions_ranking(db)


@router.get("/health")
def institution_health(
    institution_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    inst = db.query(Institution).filter(Institution.id == scoped_id).first()
    health = compute_institution_health(db, scoped_id)
    if inst:
        health["institution_name"] = inst.name
        health["institution_acronym"] = inst.acronym
    return health


# ─── Track 2 & 3: AI Insights ────────────────────────────────────────────────

@router.get("/insights")
def domain_insights(
    institution_id: int = Query(...),
    domain: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    effective_domain = _effective_domain(current_user, domain)
    kpi_data = get_latest_kpis(db, scoped_id, effective_domain)

    inst = db.query(Institution).filter(Institution.id == scoped_id).first()
    inst_name = inst.name if inst else "Établissement"
    domain_label = DOMAIN_LABELS.get(effective_domain or domain, domain)

    return generate_domain_insights(
        kpi_data=kpi_data,
        domain=effective_domain or domain,
        institution_name=inst_name,
        domain_label=domain_label,
    )


@router.post("/", response_model=KPIRecordResponse)
def create_kpi_record(
    payload: KPIRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(payload.institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")

    if current_user.domain_scope and payload.domain != current_user.domain_scope:
        raise HTTPException(
            status_code=403,
            detail=f"Votre compte est limité au domaine '{current_user.domain_scope}'"
        )

    data = payload.model_dump()
    data["institution_id"] = scoped_id
    data["created_by"] = current_user.id
    record = KPIRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
