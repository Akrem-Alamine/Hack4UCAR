from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.department import Department
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/departments", tags=["Départements"])


class DepartmentCreate(BaseModel):
    institution_id: int
    name: str
    code: str
    domain: str


class DepartmentResponse(BaseModel):
    id: int
    institution_id: int
    name: str
    code: str
    domain: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(
    institution_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Department).filter(Department.is_active == True)
    if current_user.role.value != "super_admin":
        query = query.filter(Department.institution_id == current_user.institution_id)
    elif institution_id:
        query = query.filter(Department.institution_id == institution_id)
    return query.order_by(Department.name).all()


@router.post("/", response_model=DepartmentResponse)
def create_department(
    payload: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dept = Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}")
def deactivate_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Département introuvable")
    dept.is_active = False
    db.commit()
    return {"message": "Département désactivé"}
