from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

app = Celery("ucar", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

app.conf.beat_schedule = {
    "check-alerts-every-hour": {
        "task": "app.worker.task_check_alerts",
        "schedule": crontab(minute=0),
    },
}


@app.task
def task_check_alerts():
    from app.core.database import SessionLocal
    from app.services.alert_service import run_alert_check
    db = SessionLocal()
    try:
        alerts = run_alert_check(db)
        return f"{len(alerts)} nouvelles alertes"
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
