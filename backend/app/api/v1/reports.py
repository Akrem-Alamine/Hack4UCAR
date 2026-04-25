import os
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.report import Report, ReportFormat, ReportStatus
from app.schemas.report import ReportRequest, ReportResponse
from app.dependencies.auth import get_current_user, get_scoped_institution_id
from app.services.report_service import process_report

router = APIRouter(prefix="/reports", tags=["Rapports"])


@router.get("/", response_model=list[ReportResponse])
def list_reports(
    institution_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(institution_id, current_user)
    query = db.query(Report)
    if scoped_id:
        query = query.filter(Report.institution_id == scoped_id)
    return query.order_by(Report.created_at.desc()).all()


@router.post("/", response_model=ReportResponse)
def request_report(
    payload: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_id = get_scoped_institution_id(payload.institution_id, current_user)
    if not scoped_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet établissement")

    report = Report(
        institution_id=scoped_id,
        type=payload.type,
        period_label=payload.period_label,
        format=payload.format,
        status=ReportStatus.pending,
        generated_by=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    background_tasks.add_task(_run_report, report.id)
    return report


def _run_report(report_id: int):
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        process_report(db, report_id)
    finally:
        db.close()


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    if current_user.role.value != "super_admin" and report.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce rapport")

    if report.status != ReportStatus.ready or not report.file_path:
        raise HTTPException(status_code=400, detail="Rapport non prêt")
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le serveur")

    media_type = "application/pdf" if report.format == ReportFormat.pdf else \
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ext = "pdf" if report.format == ReportFormat.pdf else "xlsx"
    filename = f"rapport_{report.period_label}_{report.id}.{ext}"

    return FileResponse(report.file_path, media_type=media_type, filename=filename)
