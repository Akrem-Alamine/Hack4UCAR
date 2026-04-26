import re
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.kpi import KPIRecord
from app.models.institution import Institution
from app.ai.anomaly import detect_anomaly, forecast_linear

# Standard semester format — only these period labels are used for latest/trend logic
_STANDARD_PERIOD = re.compile(r"^\d{4}-\d{4} S[12]$")


def _is_standard(label: str | None) -> bool:
    return bool(_STANDARD_PERIOD.match(label or ""))


def _sort_key(record: KPIRecord):
    """Standard-format periods rank above garbage ones; within each group, newest first."""
    ps = record.period_start or date(1970, 1, 1)
    return (0 if _is_standard(record.period_label) else 1, -ps.toordinal())


def get_latest_kpis(db: Session, institution_id: int | None, domain: str | None = None) -> list[dict]:
    query = (
        db.query(KPIRecord, Institution.name, Institution.acronym)
        .join(Institution, KPIRecord.institution_id == Institution.id)
    )

    if institution_id:
        query = query.filter(KPIRecord.institution_id == institution_id)
    if domain:
        query = query.filter(KPIRecord.domain == domain)

    raw = query.all()
    # Sort: standard-semester records first (newest first), then non-standard last
    all_records = sorted(raw, key=lambda x: _sort_key(x[0]))

    seen = set()
    results = []
    for record, inst_name, inst_acronym in all_records:
        key = (record.institution_id, record.indicator_key)
        if key in seen:
            continue
        seen.add(key)

        historical = (
            db.query(KPIRecord.value, KPIRecord.period_label)
            .filter(
                KPIRecord.institution_id == record.institution_id,
                KPIRecord.indicator_key == record.indicator_key,
                KPIRecord.id != record.id,
            )
            .order_by(KPIRecord.period_start.asc())
            .all()
        )
        hist_values = [r.value for r in historical]
        anomaly_info = detect_anomaly(hist_values, record.value)

        results.append({
            "id": record.id,
            "institution_id": record.institution_id,
            "institution_name": inst_name,
            "institution_acronym": inst_acronym,
            "domain": record.domain,
            "indicator_key": record.indicator_key,
            "value": record.value,
            "unit": record.unit,
            "period_label": record.period_label,
            "is_anomaly": anomaly_info["is_anomaly"],
            "z_score": anomaly_info["z_score"],
            "anomaly_direction": anomaly_info["direction"],
        })

    return results


def get_kpi_trend(db: Session, institution_id: int, indicator_key: str) -> dict:
    records = (
        db.query(KPIRecord)
        .filter(
            KPIRecord.institution_id == institution_id,
            KPIRecord.indicator_key == indicator_key,
        )
        .order_by(KPIRecord.period_start.asc())
        .all()
    )
    # Only include standard-semester records in trend charts
    records = [r for r in records if _is_standard(r.period_label)]

    if not records:
        return {}

    values = [r.value for r in records]
    labels = [r.period_label for r in records]
    forecast_data = forecast_linear(values, labels)

    return {
        "institution_id": institution_id,
        "indicator_key": indicator_key,
        "unit": records[0].unit,
        "historical_values": values,
        "historical_labels": labels,
        "forecast_values": forecast_data["forecast"],
        "forecast_labels": forecast_data["labels"],
        "trend": forecast_data["trend"],
        "slope": forecast_data["slope"],
    }


def get_cross_institution_comparison(db: Session, indicator_key: str, period_label: str | None = None) -> list[dict]:
    query = db.query(KPIRecord, Institution.name, Institution.acronym).join(
        Institution, KPIRecord.institution_id == Institution.id
    ).filter(KPIRecord.indicator_key == indicator_key)

    if period_label:
        query = query.filter(KPIRecord.period_label == period_label)

    records = query.order_by(KPIRecord.value.desc()).all()
    return [
        {
            "institution_id": r.institution_id,
            "institution_name": name,
            "institution_acronym": acronym,
            "value": r.value,
            "unit": r.unit,
            "period_label": r.period_label,
        }
        for r, name, acronym in records
    ]
