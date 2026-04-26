import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.institution import Institution
from app.models.department import Department
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.schemas.institution import InstitutionCreate, InstitutionResponse, InstitutionSummary
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/institutions", tags=["Établissements"])

_DEPT_TEMPLATES = [
    {"name": "Académique",               "code": "ACAD",   "domain": "academic",   "email_prefix": "academique"},
    {"name": "Finance",                  "code": "FIN",    "domain": "finance",    "email_prefix": "finance"},
    {"name": "Ressources Humaines",      "code": "RH",     "domain": "hr",         "email_prefix": "rh"},
    {"name": "Insertion Professionnelle","code": "INSERT", "domain": "insertion",  "email_prefix": "insertion"},
    {"name": "ESG / RSE",                "code": "ESG",    "domain": "esg",        "email_prefix": "esg"},
    {"name": "Recherche",                "code": "RECH",   "domain": "research",   "email_prefix": "recherche"},
]


def _acronym_key(acronym: str) -> str:
    return acronym.lower().replace("'", "").replace(" ", "").replace("'", "")


@router.get("/", response_model=list[InstitutionResponse])
def list_institutions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value == "super_admin":
        institutions = db.query(Institution).filter(Institution.is_active == True).order_by(Institution.name).all()
    else:
        institutions = (
            db.query(Institution)
            .filter(Institution.id == current_user.institution_id, Institution.is_active == True)
            .all()
        )
    return institutions


@router.get("/summary", response_model=list[InstitutionSummary])
def list_institutions_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value == "super_admin":
        return db.query(Institution).filter(Institution.is_active == True).order_by(Institution.name).all()
    return (
        db.query(Institution)
        .filter(Institution.id == current_user.institution_id)
        .all()
    )


@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value != "super_admin" and current_user.institution_id != institution_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Établissement introuvable")
    return inst


@router.post("/", status_code=201)
def create_institution(
    payload: InstitutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Super admin only. Creates an institution and provisions:
    - 6 departments (academic, finance, hr, insertion, esg, research)
    - 1 president account
    - 6 department accounts
    Returns the institution, created accounts, and a one-time default password.
    """
    if current_user.role.value != "super_admin":
        raise HTTPException(status_code=403, detail="Réservé au super administrateur")

    acronym = payload.acronym.strip()
    if db.query(Institution).filter(Institution.acronym == acronym).first():
        raise HTTPException(status_code=409, detail=f"Le sigle « {acronym} » est déjà utilisé")

    inst = Institution(
        name=payload.name.strip(),
        acronym=acronym,
        type=payload.type.strip(),
        city=payload.city.strip(),
    )
    db.add(inst)
    db.flush()

    for t in _DEPT_TEMPLATES:
        db.add(Department(
            institution_id=inst.id,
            name=t["name"],
            code=t["code"],
            domain=t["domain"],
        ))

    password = secrets.token_urlsafe(10)
    key = _acronym_key(acronym)

    accounts = []
    president = User(
        email=f"president@{key}.tn",
        hashed_password=hash_password(password),
        first_name="Président",
        last_name=acronym,
        role=UserRole.president,
        institution_id=inst.id,
    )
    db.add(president)
    accounts.append({"email": president.email, "role": "president", "domain": None})

    for t in _DEPT_TEMPLATES:
        u = User(
            email=f"{t['email_prefix']}@{key}.tn",
            hashed_password=hash_password(password),
            first_name=t["name"],
            last_name=acronym,
            role=UserRole.department,
            institution_id=inst.id,
            domain_scope=t["domain"],
        )
        db.add(u)
        accounts.append({"email": u.email, "role": "department", "domain": t["domain"]})

    db.commit()
    db.refresh(inst)

    return {
        "institution": {
            "id": inst.id,
            "name": inst.name,
            "acronym": inst.acronym,
            "type": inst.type,
            "city": inst.city,
            "created_at": inst.created_at.isoformat(),
        },
        "password": password,
        "accounts": accounts,
    }
