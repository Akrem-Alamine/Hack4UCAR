from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.alert import AlertRuleCreate, AlertRuleResponse, AlertResponse
from app.dependencies.auth import get_current_user, get_scoped_institution_id
from app.services.alert_service import get_alerts, acknowledge_alert, run_alert_check
from app.models.alert import AlertRule

router = APIRouter(prefix="/alerts", tags=["Alertes"])


@router.get("/", response_model=list[dict])
def list_alerts(
    institution_id: Optional[int] = Query(None),
    unresolved_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    return get_alerts(db, scoped_id, unresolved_only)


@router.post("/{alert_id}/acknowledge")
def ack_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = acknowledge_alert(db, alert_id, current_user.id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return {"message": "Alerte acquittée avec succès", "alert_id": alert_id}


@router.post("/check")
def trigger_alert_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_alerts = run_alert_check(db)
    return {"message": f"{len(new_alerts)} nouvelle(s) alerte(s) déclenchée(s)", "count": len(new_alerts)}


@router.get("/rules", response_model=list[AlertRuleResponse])
def list_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AlertRule).filter(AlertRule.is_active == True)
    if current_user.role.value != "super_admin":
        query = query.filter(
            (AlertRule.institution_id == current_user.institution_id) | (AlertRule.institution_id == None)
        )
    return query.all()


@router.post("/rules", response_model=AlertRuleResponse)
def create_rule(
    payload: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = AlertRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
