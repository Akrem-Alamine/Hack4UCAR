"""
Track 3 — Celery worker with scheduled automated tasks.
- Hourly: alert threshold checking
- Weekly: report generation for all institutions
- Monthly: full institutional report
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

app = Celery("ucar", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

app.conf.beat_schedule = {
    # Track 2: check alerts every hour
    "check-alerts-every-hour": {
        "task": "app.worker.task_check_alerts",
        "schedule": crontab(minute=0),
    },
    # Track 3: generate weekly reports every Monday at 7am
    "weekly-reports-monday": {
        "task": "app.worker.task_generate_weekly_reports",
        "schedule": crontab(hour=7, minute=0, day_of_week=1),
    },
    # Track 3: generate monthly reports on the 1st of each month at 6am
    "monthly-reports-first": {
        "task": "app.worker.task_generate_monthly_reports",
        "schedule": crontab(hour=6, minute=0, day_of_month=1),
    },
}

app.conf.timezone = "Africa/Tunis"


@app.task
def task_check_alerts():
    from app.core.database import SessionLocal
    from app.services.alert_service import run_alert_check
    db = SessionLocal()
    try:
        alerts = run_alert_check(db)
        return f"{len(alerts)} nouvelles alertes déclenchées"
    finally:
        db.close()


@app.task
def task_generate_report(report_id: int):
    from app.core.database import SessionLocal
    from app.services.report_service import process_report
    db = SessionLocal()
    try:
        process_report(db, report_id)
    finally:
        db.close()


@app.task
def task_generate_weekly_reports():
    """Track 3: Auto-generate weekly PDF reports for all active institutions."""
    from datetime import date
    from app.core.database import SessionLocal
    from app.models.institution import Institution
    from app.models.report import Report
    from app.models.user import User, UserRole
    from app.services.report_service import process_report

    db = SessionLocal()
    try:
        institutions = db.query(Institution).filter(Institution.is_active == True).all()
        period = f"Semaine du {date.today().strftime('%d/%m/%Y')}"
        created = 0

        for inst in institutions:
            # Use the institution's super_admin or first president as created_by
            admin = (
                db.query(User)
                .filter(User.role == UserRole.super_admin)
                .first()
            )
            if not admin:
                continue

            report = Report(
                institution_id=inst.id,
                type="weekly",
                period_label=period,
                format="pdf",
                status="pending",
                generated_by=admin.id,
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            process_report(db, report.id)
            created += 1

        return f"{created} rapports hebdomadaires générés"
    finally:
        db.close()


@app.task
def task_generate_monthly_reports():
    """Track 3: Auto-generate comprehensive monthly reports."""
    from datetime import date
    from app.core.database import SessionLocal
    from app.models.institution import Institution
    from app.models.report import Report
    from app.models.user import User, UserRole
    from app.services.report_service import process_report

    db = SessionLocal()
    try:
        institutions = db.query(Institution).filter(Institution.is_active == True).all()
        month_label = date.today().strftime("%B %Y")
        created = 0

        for inst in institutions:
            admin = db.query(User).filter(User.role == UserRole.super_admin).first()
            if not admin:
                continue

            report = Report(
                institution_id=inst.id,
                type="monthly",
                period_label=month_label,
                format="pdf",
                status="pending",
                generated_by=admin.id,
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            process_report(db, report.id)
            created += 1

        return f"{created} rapports mensuels générés"
    finally:
        db.close()
