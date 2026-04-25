from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.institution import Institution
from app.models.user import User
from app.schemas.institution import InstitutionResponse, InstitutionSummary
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/institutions", tags=["Établissements"])


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
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Établissement introuvable")
    return inst
